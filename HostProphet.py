class HostProphet():

    def __init__(self,ip,measure,ifid):
        self.__ip = ip
        self.__anomalous = False
        self.__measure = measure
        self.__ifid = ifid
        self.__fourier = None
        self.__trend = None
        self.__seasonality = None
        self.__totalCheck = 0
    
    #####################################Getters
    
    def getIP(self):
        return self.__ip
    
    def isAnomalous(self):
        return self.__anomalous
    
    def getMeasure(self):
        return self.__measure
    
    def getIFid(self):
        return self.__ifid

    def getFourier(self):
        return self.__fourier
    
    def getTrend(self):
        return self.__trend

    def getTotalCheck(self):
        return self.__totalCheck    
    
    def getSeasonality(self):
        return self.__seasonality

    #####################################Setters
    
    def setTrend(self,trend):
        self.__trend = trend
    
    def setSeasonality(self,seasonality):
        self.__seasonality = seasonality
    
    def setFourier(self,fourier):
        self.__fourier = fourier
    
    def incTotalCheck(self):
        self.__totalCheck += 1
    
    def resetTotalCheck(self):
        self.__totalCheck = 0

    def setAnomalous(self,val):
        self.__anomalous = val
    

    
