import sys
import config as cf
from utils import incGeneralStats

class RSI():

    def __init__(self,series,period,host,p_type,interface,date,statsRSI):
        self.__period = period
        self.__host = host
        self.__p_type = p_type
        self.__isPrinted = False
        self.__interface=interface
        self.__a_type= "mac" if(p_type.find("mac")!=-1) else "ip"
        self.__firstRSI(series,date,statsRSI)

    def __checkAnomaly(self,rsiValue,date,statsRSI,RSI):

        incGeneralStats(statsRSI, self.__host, self.__p_type, self.__a_type)

        if (rsiValue > cf.RSI_threshold):
            if(not self.__isPrinted and cf.verbose):
                print("%-8s %-18s %-25s %-5s %-25s %-16s %.1f\n"
                    % ("START",self.__p_type,self.__host,self.__interface,date,"RSI",RSI),end = '',flush = True)
                self.__isPrinted = True
            statsRSI["general"][self.__p_type]['anomalies']+=1
            statsRSI["host"][self.__host][self.__p_type]['anomalies']+=1
            
        elif (self.__isPrinted and cf.verbose):
            print("%-8s %-18s %-25s %-5s %-25s %-16s\n"
                % ("END",self.__p_type,self.__host,self.__interface,date,"RSI"),end = '',flush = True)
            self.__isPrinted = False

    def __checkDivisionByZero(self,numerator, denumerator):
        if(denumerator == 0.0 and  numerator == 0.0):
            return 50.0
        elif(denumerator == 0.0):
            return 100.0
        return -1

    def __firstRSI(self,series,date,statsRSI):
        if(self.__period<=0):
            return
        if(len(series)<self.__period+1):
            return
        sumpos = 0.0
        sumneg = 0.0
        dim = len(series)-1
        for j in range(dim):
            diff = series[dim-j] - series[dim-(j+1)]
            if diff > 0:
                sumpos += diff
            else:
                sumneg += diff
        avgGain = sumpos / self.__period
        avgLoss = (-sumneg) / self.__period
        RSI = self.__checkDivisionByZero(avgGain,avgLoss)
        if(RSI == -1):
            rs = avgGain / avgLoss
            RSI = 100 - (100 / (1 + rs))
        self.__smoothedAvgGain = avgGain
        self.__smoothedAvgLoss = avgLoss
        self.__last = series[-1]
        self.__checkAnomaly(RSI,date,statsRSI,RSI)

    def next(self,currentValue,date,statsRSI):
        currentGain = 0.0
        currentLoss = 0.0
        diff = currentValue-self.__last
        if (diff > 0):
            currentGain = diff
        else:
            currentLoss = -diff
        self.__last = currentValue
        self.__smoothedAvgGain = (self.__smoothedAvgGain * (self.__period-1) + currentGain) / self.__period 
        self.__smoothedAvgLoss = (self.__smoothedAvgLoss * (self.__period-1) + currentLoss) / self.__period
        RSI = self.__checkDivisionByZero(self.__smoothedAvgGain,self.__smoothedAvgLoss)
        if(RSI == -1):
            smoothedRS = self.__smoothedAvgGain / self.__smoothedAvgLoss
            RSI = 100 - (100 / (1 + smoothedRS))
        self.__checkAnomaly(RSI,date,statsRSI,RSI)