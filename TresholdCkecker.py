import config as cf
from utils import incGeneralStats

anomalyHost = [] 

def checkTreshold (actual, a_type, host, ifid, stats, date, host_type, th_val):
    
    incGeneralStats(stats, host, a_type, host_type)

    hostKey = host+'|'+ifid+'|'+a_type
    if(actual >= th_val):
        if(not (hostKey in anomalyHost) and cf.verbose):
            print("---> ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: TR-VAL %.1f\n"
                % (a_type,host,ifid,date, min(10000.0, actual)),end = '',flush = True)
            anomalyHost.append(hostKey)
        stats["general"][a_type]['anomalies']+=1
        stats["host"][host][a_type]['anomalies']+=1
        return False
            
    elif (hostKey in anomalyHost and cf.verbose):
        print("<--- ANOMALY TYPE: %-22s HOST/MAC: %-30s IF: %-5s DATE: %-25s METHOD: TR-VAL\n"
            % (a_type,host,ifid,date),end = '',flush = True)
        anomalyHost.remove(hostKey)
    
    return True