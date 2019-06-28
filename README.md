# Network-Time-Series-Analyzer
Hybrid anomaly-based intrusion detection system  

DEPENDENCIES INSTALLATION  

Only for Ubuntu < 16.10, execute: sudo add-apt-repository ppa:deadsnakes/ppa  
sudo apt-get update  
sudo apt-get install python3.6  

python3.6 -m pip install pystan    
python3.6 -m pip install fbprophet  
python3.6 -m pip install influxdb  
python3.6 -m pip install schedule  

OTHER DEPENDENCIES  

influxdb >= 1.7.6  
ntopng >= 3.9.190625  

USAGE  

The first time execute: ./configure.sh  
python3.6 ./net_tisean.py [-h] [-c] [-p] [-f FILE] [-d DIR]  

BASIC EXAMPLE  

python3.6 ./net_tisean.py -p -f results.txt  

