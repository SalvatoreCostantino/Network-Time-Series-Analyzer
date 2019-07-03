# Network Time Series Analyzer
Hybrid anomaly-based intrusion detection system  

<br/>**DEPENDENCIES INSTALLATION**  

Only for Ubuntu < 16.10, execute: sudo add-apt-repository ppa:deadsnakes/ppa  
sudo apt-get update  
sudo apt-get install python3.6  

python3.6 -m pip install numpy  
python3.6 -m pip install matplotlib  
python3.6 -m pip install pandas  
python3.6 -m pip install pystan    
python3.6 -m pip install fbprophet  
python3.6 -m pip install influxdb  
python3.6 -m pip install schedule  

<br/>**OTHER DEPENDENCIES**  

influxdb >= 1.7.6  
ntopng >= 3.9.190625  
BCC (https://github.com/iovisor/bcc/blob/master/INSTALL.md)  

<br/>**USAGE**  

The first time execute: ./configure.sh  
python3.6 ./net_tisean.py [-h] [-c] [-p] [-f FILE] [-d DIR] [-t TIME]  

<br/>**BASIC EXAMPLE** 

python3.6 ./net_tisean.py -p -f results.txt -t '2019-06-28T17:28:00Z'

