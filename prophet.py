import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt
from fbprophet.diagnostics import cross_validation,performance_metrics
import numpy as np
import sys
import config as cf
from decorator import suppress_stdout_stderr
from utils import incGeneralStats

statsProphet = {"general":{}, "host":{}}

def AnomalyChecker(actual,predicted,hostProphet, client,categories,metric,influxQuery):

    t_type = hostProphet.getMeasure()
    host_mac = hostProphet.getIP()
    ifid = hostProphet.getIFid()
    
    incGeneralStats(statsProphet, host_mac, t_type, "ip")

    checked=''
    if actual['y'] > predicted['yhat_upper'] or actual['y'] < predicted['yhat_lower']:
        if cf.checkCat:
            if(influxQuery(client, actual['ds'], categories, ifid, host_mac, metric)>0):
                checked='+NDPI'
        if(not cf.checkCat or checked == '+NDPI'):
            statsProphet["general"][t_type]['anomalies']+=1
            statsProphet["host"][host_mac][t_type]['anomalies']+=1

        if not (hostProphet.isAnomalous() and cf.verbose):
            print("%-8s %-18s %-25s %-5s %-25s %-16s\n"
                % ("START",t_type, host_mac, ifid, actual['ds'],"PROPHET"+checked),end='',flush=True)
            hostProphet.setAnomalous(True)
    elif hostProphet.isAnomalous() and cf.verbose:
        
        if cf.checkCat:
            meth = "PROPHET+NDPI"
        else:
            meth = "PROPHET"
        
        print("%-8s %-18s %-25s %-5s %-25s %-16s\n"
            % ("END",t_type, host_mac,ifid,actual['ds'],meth),end='',flush=True)
        hostProphet.setAnomalous(False)

def isWeekendDay(ds):
    date = pd.to_datetime(ds)
    return date.dayofweek >= 5

def noNegative(val):
    val = val if val >=0 else 0
    return val

def rmse(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def prophet(df,dimVL,frequency, hostProphet, client, categories, metric, influxQuery, showGraph=False):
    df['weekend'] = df['ds'].apply(isWeekendDay)
    df['no_weekend'] = ~df['ds'].apply(isWeekendDay)
    df_training = df[:-(dimVL+cf.predictedPoint)]
    df_test = df[-(dimVL+cf.predictedPoint):-cf.predictedPoint]
  
    italianHolidays2019 = pd.DataFrame({
        'holiday': 'italianHolidays2019',
        'ds': pd.to_datetime(['2019-01-01', '2019-01-06', '2019-04-21',
                            '2019-04-22','2019-04-25','2019-05-01',
                            '2019-06-02','2019-08-15','2019-11-01','2019-12-08',
                            '2019-12-24','2019-12-25','2019-12-26','2019-12-31'])
    })

    if (hostProphet.getTrend() == None or hostProphet.getTotalCheck() == cf.validationTime):
        fr, cp, ss = modelSelection(df_training, df_test, min(2*dimVL,cf.dim_vlset),
            dimVL,italianHolidays2019,frequency)
        hostProphet.setTrend(cp)
        hostProphet.setFourier(fr)
        hostProphet.setSeasonality(ss)
        hostProphet.resetTotalCheck()

    fcst,m = fit_predict(df[:-cf.predictedPoint],italianHolidays2019,
        hostProphet.getFourier(), hostProphet.getTrend(), hostProphet.getSeasonality() ,cf.totPredPoint,frequency)

    j=cf.predictedPoint
    i=cf.totPredPoint
    point = []

    while i > 0 and j > 0:
        if(pd.to_datetime(df.iloc[-j]['ds']) == fcst.iloc[-i]['ds']):
            point.append(df.iloc[-j])
            AnomalyChecker(df.iloc[-j], fcst.iloc[-i], hostProphet, client,categories,metric,influxQuery)
            i-=1
            j-=1
        elif pd.to_datetime(df.iloc[-j]['ds']) > fcst.iloc[-i]['ds']:
            i-=1
        else:
            j-=1
    
    if(showGraph):
        m.plot(fcst)
        plt.plot([pd.to_datetime(point[i]['ds']) for i in range(0,len(point))],
            [point[i]['y'] for i in range(0,len(point))],"ro-",ms=3)
        plt.savefig(cf.graphDir+ hostProphet.getIP() +"_"+ hostProphet.getMeasure() +".png")
        plt.close()



def modelSelection(df_training, df_test,dimTotTest,dimTest, holiday,frequency):
    fr_hpar = [(7,13)]
    cp_hpar = [0.05, 0.2]
    ss_hpar = [10, 25]
    b_rmse = float('inf')

    for i in range(len(fr_hpar)):
        for j in range (len(cp_hpar)):
            for k in range (len(ss_hpar)):
                fcst,_ = fit_predict(df_training,holiday,fr_hpar[i],cp_hpar[j],ss_hpar[k],dimTest,frequency)
                test, pred = checkDate(df_test,fcst[-dimTotTest:],dimTotTest, dimTest)
                rmse_val = rmse(test, pred)
                if (rmse_val < b_rmse):
                    b_hpar = [i,j,k]
                    b_rmse = rmse_val
  
    return fr_hpar[b_hpar[0]], cp_hpar[b_hpar[1]], ss_hpar[b_hpar[2]]

def checkDate(df_test, df_fc, dimTotTest, dimTest):
    j = dimTest
    i = dimTotTest
    test = []
    pred = []

    while i > 0 and j > 0:
        if(pd.to_datetime(df_test.iloc[-j]['ds']) == df_fc.iloc[-i]['ds']):
            test.append(df_test.iloc[-j]['y'])
            pred.append(df_fc.iloc[-i]['yhat'])
            i-=1
            j-=1
        elif pd.to_datetime(df_test.iloc[-j]['ds']) > df_fc.iloc[-i]['ds']:
            i-=1
        else:
            j-=1
     
    return (test,pred)


def fit_predict(df_training, holiday, fr, cp, ss, dimPred, frequency):
    
    m = Prophet(holidays=holiday, interval_width=0.99, yearly_seasonality=False, weekly_seasonality=fr[1], 
        daily_seasonality=False, changepoint_prior_scale=cp, holidays_prior_scale=15, 
        seasonality_prior_scale=ss, seasonality_mode='multiplicative')
    m.add_seasonality(name='work_days', period=1, fourier_order=fr[0], condition_name='no_weekend')
    m.add_seasonality(name='weekend_days', period=1, fourier_order=fr[0], condition_name='weekend')
    with suppress_stdout_stderr():
        m.fit(df_training)
    future = m.make_future_dataframe(periods=dimPred, freq=frequency)
    future['weekend'] = future['ds'].apply(isWeekendDay)
    future['no_weekend'] = ~future['ds'].apply(isWeekendDay)
    fcst = m.predict(future)
    fcst['yhat'] = fcst['yhat'].apply(noNegative)
    fcst['yhat_lower'] = fcst['yhat_lower'].apply(noNegative)
    return fcst, m