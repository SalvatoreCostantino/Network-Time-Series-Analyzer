# Network-Time-Series-Analyzer
Hybrid anomaly-based intrusion detection system  


DEPENDENCIES INSTALLATION  

sudo apt-get update  
sudo apt-get install python3.6  

python3.6 -m pip install fbprophet  
python3.6 -m pip install influxdb  
python3.6 -m pip install schedule  


USAGE  

python3.6 ./net_tisean.py [-h] [-c] [-p] [-f FILE] [-d DIR]  


BASIC EXAMPLE  

python3.6 ./net_tisean.py -p -f results.txt  

