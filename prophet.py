import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt
from fbprophet.diagnostics import cross_validation,performance_metrics
import numpy as np
import sys
import config as cf
from decorator import suppress_stdout_stderr

anomalyHost = [] 
statsProphet = {"general":{}, "host":{}}

def AnomalyChecker(actual,predicted,t_type,host_mac,ifid,client,categories,metric,influxQuery):

    if t_type in statsProphet["general"]:
        statsProphet["general"][t_type]['total']+=1
    else:
        statsProphet["general"].update({t_type:{"total": 1, "anomalies" : 0}})

    if host_mac in statsProphet["host"]:
        if t_type in statsProphet["host"][host_mac]:
            statsProphet["host"][host_mac][t_type]['total']+=1
        else:
            statsProphet["host"][host_mac].update({t_type:{"total": 1, "anomalies" : 0}})
    else:
        statsProphet["host"].update({host_mac:{t_type:{"total": 1, "anomalies" : 0},"type":"ip"}})    

    checked=''
    if abs(actual['y']-predicted['yhat']) > cf.prophet_mul*abs(predicted['yhat_upper']-predicted['yhat_lower']):
        if cf.checkCat:
            if(influxQuery(client, actual['ds'], categories, ifid, host_mac, metric)>0):
                checked='+NDPI'
        if(not cf.checkCat or checked == '+NDPI'):
            statsProphet["general"][t_type]['anomalies']+=1
            statsProphet["host"][host_mac][t_type]['anomalies']+=1

        if not (host_mac in anomalyHost and cf.verbose):
            print("---> ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: %s\n"
                % (t_type, host_mac,ifid,actual['ds'],"PROPHET"+checked),end='',flush=True)
            anomalyHost.append(host_mac)
    elif host_mac in anomalyHost and cf.verbose:
        print("<--- ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: PROPHET\n"
            % (t_type, host_mac,ifid,actual['ds']),end='',flush=True)
        anomalyHost.remove(host_mac)

def resetProphetAnomalies():
    global anomalyHost
    anomalyHost = []

def isWeekendDay(ds):
    date = pd.to_datetime(ds)
    return date.dayofweek >= 5

def rmse(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def prophet(df,dimVL,frequency,t_type, host_mac, ifid, client,categories,metric,influxQuery,showGraph=False):
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

    fr, cp, ss = modelSelection(df_training, df_test, dimVL,italianHolidays2019,frequency)
    fcst,m = fit_predict(df[:-cf.predictedPoint],italianHolidays2019,fr,cp,ss,cf.predictedPoint,frequency)

    if(showGraph):
        m.plot(fcst)
        plt.plot([pd.to_datetime(df.iloc[-i]['ds']) for i in range(1,cf.predictedPoint+1)],
            [df.iloc[-i]['y'] for i in range(1,cf.predictedPoint+1)],"ro-",ms=3)
        plt.savefig(cf.graphDir+host_mac+"_"+t_type+".png")
        plt.close()

    for i in range(1,cf.predictedPoint+1):
        AnomalyChecker(df.iloc[-i], fcst.iloc[-i], t_type,host_mac,ifid,client,categories,metric,influxQuery)

def modelSelection(df_training, df_test,dimTest,holiday,frequency):
    fr_hpar = [(7,13)]
    cp_hpar = [0.05, 0.2]
    ss_hpar = [10, 25]
    b_rmse = float('inf')

    for i in range(len(fr_hpar)):
        for j in range (len(cp_hpar)):
            for k in range (len(ss_hpar)):
                fcst,_ = fit_predict(df_training,holiday,fr_hpar[i],cp_hpar[j],ss_hpar[k],dimTest,frequency)
                rmse_val = rmse(df_test['y'],fcst['yhat'][-dimTest:])
                if (rmse_val < b_rmse):
                    b_hpar = [i,j,k]
                    b_rmse = rmse_val
  
    return fr_hpar[b_hpar[0]], cp_hpar[b_hpar[1]], ss_hpar[b_hpar[2]]


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
    
    return fcst, m