from math import sqrt
import config as cf
import os

def incGeneralStats(stats, host, anomaly_type, host_type):
    
    if anomaly_type in stats["general"]:
            stats["general"][anomaly_type]['total']+=1
    else:
        stats["general"].update({anomaly_type:{"total": 1, "anomalies" : 0}})

    if host in stats["host"]:
        if anomaly_type in stats["host"][host]:
            stats["host"][host][anomaly_type]['total']+=1
        else:
            stats["host"][host].update({anomaly_type:{"total": 1, "anomalies" : 0}})
    else:
        stats["host"].update({host:{anomaly_type:{"total": 1, "anomalies" : 0},"type":host_type}})


def updateGeneralStats(currStats,cumStats,method):
    for a_type in currStats:
        if a_type in cumStats[method]:
            cumStats[method][a_type]['total']+=currStats[a_type]['total']
            cumStats[method][a_type]['anomalies']+=currStats[a_type]['anomalies']
        else:
            cumStats[method].update({a_type:currStats[a_type]})


def updateHostStats(currStats,cumStats,method):
    for host in currStats:
        if host in cumStats:
            if method in cumStats[host]:
                for a_type in currStats[host]:
                    if type(currStats[host][a_type] is str):
                        continue
                    if a_type in cumStats[host][method]:
                        cumStats[host][method][a_type]["anomalies"]+=currStats[host][a_type]["anomalies"]
                        cumStats[host][method][a_type]["total"]+=currStats[host][a_type]["total"]
                    else:
                        cumStats[host][method].update({a_type:currStats[host][a_type]})
            else:
                cumStats[host].update({method:currStats[host]})
        else:
            cumStats.update({host:{method:currStats[host]}})

def updateAllHostStats(currStatsRSI,currStatsTH,cumStats):
    updateHostStats(currStatsRSI["host"],cumStats["host"],"RSI")
    updateHostStats(currStatsTH["host"],cumStats["host"],"TRESHOLD")    


def updateAllGeneralStats(currStatsRSI,currStatsTH,cumStats):
    updateGeneralStats(currStatsRSI["general"],cumStats["general"],"RSI")
    updateGeneralStats(currStatsTH["general"],cumStats["general"],"TRESHOLD")

        
def mergeStats(currStats,cumStats,method):
    updateGeneralStats(currStats["general"],cumStats["general"],method)
    updateHostStats(currStats["host"],cumStats["host"],method)



def printGeneralStats(stats):
    if(stats!={}):
        print("\n%-20s %-20s %-20s %-20s" %("TYPE","TOTAL_CHECK","ANOMALIES","METHOD"))
        for meth in stats:
            for key in stats[meth]:
                print("%-20s %-20d %-20d %-20s" %(key,stats[meth][key]['total'],stats[meth][key]['anomalies'],meth))


def HostStats(stats,scoreTable,printAll):
    score = []
    atkScore = []
    toBlock=[]
    if(stats!={}):
        if printAll:
            print("\n%-30s %-20s %-20s %-20s %-20s" %("HOST","TYPE","TOTAL_CHECK","ANOMALIES","METHOD"))
        for host in stats:
            if printAll:
                print("%-30s" %(host))
            for meth in stats[host]:
                sumScore = 0.0
                sumAtkScore = 0.0
                for aType in stats[host][meth]:
                    if type(stats[host][meth][aType]) is str:
                        continue
                    sumScore += stats[host][meth][aType]['anomalies'] * scoreTable[aType]
                    if aType.find("clt")!=-1 or aType.find("unreach_srv"):
                        sumAtkScore+=stats[host][meth][aType]['anomalies'] * scoreTable[aType]
                        
                        if(stats[host][meth][aType]['anomalies']!=0 and (meth == 'TRESHOLD' or (meth == 'PROPHET' and cf.checkCat))  
                            and host not in toBlock):
                            
                            if(stats[host][meth]["type"] == "mac"):
                                toBlock.append("mac"+host)
                            elif host.find(":")!=-1:
                                toBlock.append("ipv6"+host[:-cf.hostTrailer])
                            else:
                                toBlock.append("ipv4"+host[:-cf.hostTrailer])
                        
                    if printAll:
                        print("%-30s %-20s %-20d %-20d %-20s"
                            % ('',aType,stats[host][meth][aType]['total'], stats[host][meth][aType]['anomalies'],meth))
                
                updateScore(score,host, sumScore)
                updateScore(atkScore,host, sumAtkScore)

        score = sorted(score, key = lambda i: i['score'], reverse = True)[:cf.maxLine]
        atkScore = sorted(atkScore, key = lambda i: i['score'], reverse = True)[:cf.maxLine]

        return hostAnomalies(score,atkScore,toBlock)

def updateScore(scoreArr,host,score):
    trovato = False
    i=0
    while (not trovato and i<len(scoreArr)):
        if scoreArr[i]["hostName"] == host:
            trovato = True
            scoreArr[i]["score"]+=score
        i+=1
    if(not trovato):
        scoreArr.append({"hostName":host, "score":score})

def hostAnomalies(score,atkScore,toBlock):
    if len(atkScore)>0:
        print("\n%-30s %-20s"%("TOP ATTACKER HOST","ANOMALY SCORE"))
        for x in atkScore:
            print("%-30s %-20.2f" %(x["hostName"],x["score"]))

    if len(score)>0:
        print("\n%-30s %-20s"%("TOP ANOMALOUS HOST","ANOMALY SCORE"))
        for x in score:
            print("%-30s %-20.2f" %(x["hostName"],x["score"]))

    return toBlock


def isLocalHost(ip):
    return ip[slice(3)] == "127" or ip=="::1"


def convertDate(date):
    return str(date).split('+')[0]

def createDir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def truncate(number):
    return int(number*cf.precision) / float(cf.precision)

def checkNotZero(df,size):
    for i in range(size):
        if df['y'].iloc[i] != 0:
            return True
    return False
    
