import logging
logging.basicConfig(level=logging.CRITICAL)

from influxdb import DataFrameClient,  InfluxDBClient
from influx import influxQuery1h, influxQuery5m, statsRSI,statsTreshold
import schedule
from utils import HostStats, printGeneralStats, updateAllGeneralStats,mergeStats,updateAllHostStats, createDir
import time as tm
import os
import config as cf
import sys
import signal
from parser import parseArg

if cf.mitigation:
    import firewall as fw

from multiprocessing import Process, Queue
import queue as qu

closing = False
processes=[None, None]

            
def signal_handler(signal, frame):
    global closing
    closing=True
    print("\nclosing...")


def startRSI(client5m,printAll,cumulative_stat):
    influxQuery5m(client5m,cf.num_points5m,cf.period+1,cf.measurements5m,cf.interfaces,cf.start_time)
    updateAllHostStats(startRSI, statsTreshold, cumulative_stat)
    addresses = HostStats(cumulative_stat["host"],cf.scoreTable,printAll)
    if cf.mitigation:
        fw.block(addresses)



def ForkProcess(client1h,client5m,queue):    
    processes[0] = Process(target=influxQuery1h, 
        args=(client1h,client5m,cf.num_points1h,cf.dim_vlset,cf.measurements1h["P0"],
        cf.interfaces,queue,cf.categories,cf.p_rate,cf.start_time))
    processes[1] = Process(target=influxQuery1h, 
        args=(client1h,client5m,cf.num_points1h,cf.dim_vlset,cf.measurements1h["P1"],
        cf.interfaces,queue,cf.categories,cf.p_rate,cf.start_time))
    for proc in processes:
        proc.start()


def checkJoin(stats,queue):
    for proc in processes:
        if proc!=None:
            if(proc.is_alive()):
                try:
                    mergeStats(queue.get(timeout=1),stats,"PROPHET")
                except qu.Empty:
                    pass
                proc.join(1)


def initializeScheduler(client1h,client5m,queue,cumStats):
    for i in range(3,60,5):
        minute=str(i)
        if(len(minute)==1):
            minute=":0"+minute
        else:
            minute=":"+minute
        schedule.every().hour.at(minute).do(startRSI,client5m,False,cumStats)
    if(cf.prophet_diagnostic):
        schedule.every().hour.at(cf.minuteProphet).do(ForkProcess,client1h,client5m,queue)

f = None

def initiaizeArgs(args):
    global f

    if args.file: # se scrittura su file 
        try:
            f=open(args.file,'w')
            sys.stdout = f
        except IOError:
            print("error opening file: %s" % args.file)

    if args.time:
        cf.start_time = args.time
    
    cf.prophet_diagnostic = args.prophet
    
    if cf.prophet_diagnostic:
        
        if args.dir:
            if os.path.isdir(args.dir):
                cf.graphDir = args.dir if args.dir[-1] == '/' else args.dir + '/'
            else:
                print("directory not found: %s" % args.dir)
                createDir(cf.graphDir)
        else:
            createDir(cf.graphDir)
        
        cf.checkCat = args.cat
        cf.showGraph = args.graph
    
    cf.verbose = args.verbose
    cf.mitigation = args.xdp
    
    
def main():

    args = parseArg()

    print("net_tisean (network time series analyzer) v1.0 started")

    initiaizeArgs(args)
    
    client1h = DataFrameClient(host=cf.influxHost, port=cf.influxPort)
    client5m =  InfluxDBClient(host=cf.influxHost, port=cf.influxPort)
    
    q = None
    cumulative_stat = {"general":{"TRESHOLD":{},"RSI":{},"PROPHET":{}},"host":{}}

    if(cf.prophet_diagnostic):
        q = Queue()
    
    if cf.mitigation:
        fw.inject(cf.device)

    if(cf.start_time==None): #real-time

        original_sgint_handler = signal.signal(signal.SIGINT, signal_handler)
        initializeScheduler(client1h,client5m,q,cumulative_stat)
        print("CTRL-C to terminate")
        while(not closing):
            schedule.run_pending()
            tm.sleep(30)

            if(cf.prophet_diagnostic):
                checkJoin(cumulative_stat,q)

        if(cf.prophet_diagnostic):
            checkJoin(cumulative_stat,q)

    else:
        original_sgint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

        if(cf.prophet_diagnostic):
            ForkProcess(client1h,client5m,q)
        
        influxQuery5m(client5m,cf.num_points5m,cf.period+1,cf.measurements5m,cf.interfaces,cf.start_time)

        if(cf.prophet_diagnostic):
            for _ in range(2):
                sts = q.get()
                mergeStats(sts,cumulative_stat,"PROPHET")
        
        updateAllHostStats(statsRSI, statsTreshold, cumulative_stat)

        addresses = HostStats(cumulative_stat["host"],cf.scoreTable,True)
        if cf.mitigation:
            fw.block(addresses)

    updateAllGeneralStats(statsRSI, statsTreshold, cumulative_stat)

    printGeneralStats(cumulative_stat["general"])
    
    if cf.mitigation:
        signal.signal(signal.SIGINT,original_sgint_handler)
        fw.blocked()
        fw.eject()
    if(f!=None):
        f.close()


if __name__ == '__main__':
    main()