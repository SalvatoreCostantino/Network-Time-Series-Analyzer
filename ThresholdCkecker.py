import config as cf
from utils import incGeneralStats

anomalyHost = [] 

def checkThreshold (actual, a_type, host, ifid, stats, date, host_type, th_val):
    
    incGeneralStats(stats, host, a_type, host_type)

    hostKey = host+'|'+ifid+'|'+a_type
    if(actual > th_val):
        if(not (hostKey in anomalyHost) and cf.verbose):
            print("%-8s %-18s %-25s %-5s %-25s %-16s %.1f\n"
                % ("START",a_type,host,ifid,date,"THRESHOLD",min(10000.0, actual)),end = '',flush = True)
            anomalyHost.append(hostKey)
        stats["general"][a_type]['anomalies']+=1
        stats["host"][host][a_type]['anomalies']+=1
        return False
            
    elif (hostKey in anomalyHost and cf.verbose):
        print("%-8s %-18s %-25s %-5s %-25s %-16s\n"
                % ("END",a_type,host,ifid,date,"THRESHOLD"),end = '',flush = True)
        anomalyHost.remove(hostKey)
    
    return True