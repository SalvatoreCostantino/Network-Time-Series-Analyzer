import pandas as pd
from prophet import prophet, statsProphet
from RSI import RSI
import sys
import config as cf
import signal
from utils import isLocalHost, convertDate, truncate, checkNotZero 
import time
from TresholdCkecker import checkTreshold
from HostProphet import HostProphet


hostRSI = {} #host <-> RSI objects (one for each RSI metric)
hostPROPHET = {}
statsRSI = {"general":{},"host":{}} #RSI stats
statsTreshold = {"general":{},"host":{}} #treshold

def influxQuery5m(client, max_points, min_points ,measurements, interfaces,start_time = "now()"):
    
    for measure in measurements:

        if (measurements[measure]["name"] == "arp_packets" or  measurements[measure]["name"] == "ping_packets" or 
            measurements[measure]["name"] == "dns_packets" or measurements[measure]["name"] == "dns_errors"):
            doSum = True
        else:
            doSum = False
        
        num_den=measure.split()
        numerator = num_den[0]
        denumerator2 = None

        if(len(num_den)>=2):
            denumerator=num_den[1]
            if len(num_den) == 3:
                denumerator2 = num_den[2]    
        else:
            denumerator=numerator

    
        key = numerator.split(':')[0]
        hosts = client.query('SHOW TAG VALUES ON "ntopng" FROM "autogen"."%s" WITH KEY = "%s" LIMIT %s'
            % (numerator,key,str(cf.limitRSI)))
        
        
        m_numerator = []
        m_denumerator = []
        m_denumerator2 = []
        s_clause=""
        
        for metric in measurements[measure]["metrics"][0]:
            m_numerator.append(metric)
            s_clause += "NON_NEGATIVE_DERIVATIVE(LAST(" + metric + "), 1s) AS " + metric + ", "

        if(m_numerator[0].find("flows") == -1):
            for metric in measurements[measure]["metrics"][1]:
                m_denumerator.append(metric)
                s_clause += "NON_NEGATIVE_DERIVATIVE(LAST(" + metric + "), 1s) AS " + metric + ", "
            if ( denumerator2 != None ):
                for metric in measurements[measure]["metrics"][2]:
                    m_denumerator2.append(metric)
                    s_clause += "NON_NEGATIVE_DERIVATIVE(LAST(" + metric + "), 1s) AS " + metric + ", "
        else:
            m_denumerator = m_numerator
        
        
        s_clause = s_clause[slice(len(s_clause)-2)]

        f_clause = """"ntopng"."autogen".""" +'"'+numerator+'"'
        if(denumerator != numerator):
            f_clause += """, "ntopng"."autogen".""" +'"'+denumerator+'"'
            if(denumerator2 != None):
                f_clause += """, "ntopng"."autogen".""" +'"'+denumerator2+'"'

        p2p_metric=''
        if(numerator.find("unreachable")!=-1):
            if(m_numerator[0].find("server")!=-1):
                p2p_metric = "bytes_sent"
            else:
                p2p_metric = "bytes_rcvd"

        ips = hosts.get_points()
        for ip in ips:

            if isLocalHost(ip['value']):
                continue

            for ifid in interfaces:

                #key
                host_interface_measure = ip['value']+"|"+ifid+"|"+measurements[measure]["name"]

                if(start_time == "now()" and host_interface_measure in hostRSI):
                    w_clause = start_time + " - 5m"
                    min_points = 1
                else:
                    if(start_time == "now()"):
                        max_points=2*min_points
                    w_clause = start_time + " - " + str((max_points-1)*5) + "m AND time < "+start_time
                
                results = client.query("""  SELECT %s 
                                            FROM %s 
                                            WHERE time >= %s AND "%s"='%s' AND "ifid"='%s' 
                                            GROUP BY time(5m) fill(none) """ 
                                            % (s_clause,f_clause,w_clause,key,ip['value'],ifid))

                n_points = list(results.get_points(measurement = numerator))

                if(numerator == denumerator):
                    d_points = n_points
                else:
                    d_points = list(results.get_points(measurement = denumerator))
                    if denumerator2 != None:
                        d2_points = list(results.get_points(measurement = denumerator2))
                        if len(d_points) == 0:
                            d_points = d2_points
                            m_denumerator = []
                        elif len(d2_points) == 0:
                            d2_points = d_points
                            m_denumerator2 = []

                dim_numerator = len(n_points)
                dim_denumerator = len(d_points)
                dim_denumerator2 = len(d2_points) if denumerator2 != None else dim_numerator

                if(min(dim_numerator,dim_denumerator,dim_denumerator2) < min_points):
                    continue

                if(dim_numerator != dim_denumerator):
                    if dim_denumerator > dim_numerator:
                        d_points = d_points[-dim_numerator:]
                    else:
                        n_points=n_points[-dim_denumerator:]

                #by reference changes                
                dim_denumerator2 = len(d2_points) if denumerator2 != None else dim_denumerator

                if(dim_denumerator2 != dim_denumerator and denumerator2 != None):
                    if dim_denumerator2 > dim_denumerator:
                        d2_points = d2_points[-dim_denumerator:]
                    else:
                        n_points = n_points[-dim_denumerator2:]
                        d_points = d_points[-dim_denumerator2:]

                if p2p_metric:
                    
                    results = client.query(""" SELECT NON_NEGATIVE_DIFFERENCE(SUM("%s")) AS "%s"
                                                FROM "ntopng"."autogen"."host:p2p" 
                                                WHERE time >= %s AND "%s"='%s' AND "ifid"='%s' 
                                                GROUP BY time(5m) fill(0) """ 
                                                %(p2p_metric,p2p_metric,w_clause,key,ip['value'],ifid))

                    p2p_points = list(results.get_points(measurement = "host:p2p"))
                    
                    p2p_non_zero_points=[]
                    for i in range(len(p2p_points)):
                        if(p2p_points[i][p2p_metric] != 0):
                            p2p_non_zero_points.append(p2p_points[i]['time'])                       

                series=[]
                seriesDate=[]
                
                for i in range(len(n_points)):
                    sum_numerator = 0
                    sum_denumerator = 0

                    if(n_points[i]['time'] != d_points[i]['time']):
                        break
                    
                    if(denumerator2 != None):
                        if d_points[i]['time'] != d2_points[i]['time']:
                            break
                    
                    if(p2p_metric != ''):
                        if n_points[i]['time'] in p2p_non_zero_points:
                            break

                    try:
                        for x in m_numerator:
                            sum_numerator += n_points[i][x]
                        for x in m_denumerator:
                            sum_denumerator += d_points[i][x]
                        for x in m_denumerator2:
                            sum_denumerator += d2_points[i][x]
                    except TypeError: #portability
                        continue 

                    if (sum_denumerator >= measurements[measure]["minValue"][1]  or 
                        sum_numerator >= measurements[measure]["minValue"][0]):

                        if doSum:
                                sum_denumerator += sum_numerator
                        
                        if sum_denumerator != 0:
                            ratioValue =  truncate(sum_numerator/sum_denumerator)
                        else: 
                            continue

                        if measurements[measure]["name"].find("size")!=-1:
                            thVal = cf.packet_size_treshold
                        else:
                            thVal = cf.ratio_treshold

               
                        if( not checkTreshold(ratioValue, measurements[measure]["name"],
                            ip['value'],ifid,statsTreshold,n_points[i]['time'],"ip",thVal) or 
                            (doSum and measurements[measure]["name"] != "dns_errors" )):
                            continue

                        series.append(ratioValue)
                        if(len(series) >= min_points or w_clause == "now()-5m"):
                            seriesDate.append(n_points[i]['time'])

                if (w_clause!="now() - 5m"):
                    if (len(series) >= min_points):
                        if(start_time == "now()"):
                            rsi = RSI(series[-min_points:],min_points-1,ip['value'],measurements[measure]["name"],ifid,seriesDate[0]+"|wu",statsRSI)
                            hostRSI.update({host_interface_measure:rsi})
                        else:
                            rsi = RSI(series[:min_points],min_points-1,ip['value'],measurements[measure]["name"],ifid,seriesDate[0]+"|wu",statsRSI)
                            test_series = series[min_points:]
                            for i in range(len(test_series)):
                                rsi.next(test_series[i],seriesDate[i+1],statsRSI)
                else:
                    if(len(series)>=1):
                        hostRSI[host_interface_measure].next(series[-1],seriesDate[-1],statsRSI)

def influxQuery1h(client1h, client5m, num_points, dim_vlset, measurements,interfaces,queue,categories,
                    p_rate = 0.75,start_time=None):
    
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    #counter = 0
    #sum_time = 0
    start_time = start_time if start_time!=None else "now()"
    w_clause = start_time + " - " + str((num_points-1)) + "h AND time < "+start_time

    for measure in measurements:
        hosts = client1h.query('SHOW TAG VALUES ON "ntopng" FROM "1h"."%s" WITH KEY = "host" LIMIT %s' 
            % (measure.split()[0],str(cf.limitProphet)))
        ips = hosts.get_points()

        if(cf.checkCat):
            metric = measurements[measure]["metric"]
            metric = "bytes_sent" if (metric.find("sent")!=-1 or metric.find("client")!=-1) else "bytes_rcvd" #ndpi_cat
        else: 
            metric = None

        for ip in ips:

            if isLocalHost(ip['value']):
                continue
            
            for ifid in interfaces:
                
                results = client1h.query("""SELECT "%s" AS "y" 
                                            FROM "ntopng"."1h"."%s" 
                                            WHERE time >= %s AND "host"='%s' AND "ifid"='%s'""" 
                                            % (measurements[measure]["metric"],measure.split()[0],w_clause, ip['value'] ,ifid))
                if(results == {}):
                    continue

                df = results[measure.split()[0]]
                if(df.shape[0] >= num_points*p_rate and checkNotZero(df,df.shape[0])):
                    df = df.rename_axis('ds').reset_index()
                    df['ds'] = df['ds'].apply(convertDate)

                    host_key = ip['value']+"|"+ifid+"|"+measurements[measure]["metric"]
                    if not (host_key in hostPROPHET):                    
                        hostPROPHET.update({host_key:HostProphet(ip['value'],measurements[measure]['metric'],ifid)})
                    
                    hostProphet = hostPROPHET[host_key]

                    #start = time.time()    
                    
                    prophet(df, int(dim_vlset*(df.shape[0]/num_points)), '1H', 
                        hostProphet, client5m, categories, metric, influxNdpiCategoriesQuery,cf.showGraph) #start fitting and prediction
                    #counter +=1
                    #sum_time += (time.time() - start)

    #mean_time = (sum_time / counter) if counter != 0 else 0
    queue.put((None, statsProphet))
    queue.close()


def influxNdpiCategoriesQuery(client,date,categories, ifid, host_mac, metric):
    cat_clause=""
    for x in categories:
        cat_clause+="category = "+"'"+x+"' OR "
    cat_clause=cat_clause[slice(len(cat_clause)-4)]

    results=client.query("""SELECT SUM("%s") AS "value"
                            FROM "ntopng"."1h"."host:ndpi_categories"
                            where time = '%s' AND "ifid" = '%s' AND "host" = '%s' AND (%s)
                            GROUP BY * """
                            % (metric,date,ifid,host_mac,cat_clause))
    
    points = list(results.get_points())
    
    if(len(points)!=0):
        return points[0]['value']
    else:
        return 0
