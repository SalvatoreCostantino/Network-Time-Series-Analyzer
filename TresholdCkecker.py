import config as cf

anomalyHost = [] 

def checkTreshold (actual, a_type, host, ifid, stats, date, host_type, th_val):
    if a_type in stats["general"]:
        stats["general"][a_type]['total']+=1
    else:
        stats["general"].update({a_type:{"total": 1, "anomalies" : 0}})
    
    if host in stats["host"]:
        if a_type in stats["host"][host]:
            stats["host"][host][a_type]['total']+=1
        else:
            stats["host"][host].update({a_type:{"total": 1, "anomalies" : 0}})
    else:
        stats["host"].update({host:{a_type:{"total": 1, "anomalies" : 0},"type":host_type}})
    
    if(actual >= th_val):
        if(not (host in anomalyHost) and cf.verbose):
            print("---> ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: TR-VAL %.1f\n"
                % (a_type,host,ifid,date, min(10000.00, actual)),end = '',flush = True)
            anomalyHost.append(host)
        stats["general"][a_type]['anomalies']+=1
        stats["host"][host][a_type]['anomalies']+=1
        return False
            
    elif (host in anomalyHost and cf.verbose):
        print("<--- ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: TR-VAL\n"
            % (a_type,host,ifid,date),end = '',flush = True)
        anomalyHost.remove(host)
    
    return True

def resetTresholdAnomalies():
    global anomalyHost
    anomalyHost = []