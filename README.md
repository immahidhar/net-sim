# net-sim
Network Simulator - An internet/ethernet communication simulator.  
Developed by ***Mahidhar Reddy Narala***

Project written in Python3 language. Hence, no need to compile any code. 

## How to run

### Bridge
``` python3 bridge.py <lan-name> <num-ports>```
* python3 bridge.py cs1 6  
* python3 bridge.py cs2 4  
* python3 bridge.py cs3 3  

### Router
```python3 station.py -route iface_filepath rtable_filepath hostnames_filepath```
* python3 station.py -route ifaces/ifaces.r1 rtables/rtable.r1 hosts  
* python3 station.py -route ifaces/ifaces.r2 rtables/rtable.r2 hosts

### Station
```python3 station.py -no iface_filepath rtable_filepath hostnames_filepath```
* python3 station.py -no ifaces/ifaces.a rtables/rtable.a hosts  
* python3 station.py -no ifaces/ifaces.b rtables/rtable.b hosts  
* python3 station.py -no ifaces/ifaces.c rtables/rtable.c hosts  
* python3 station.py -no ifaces/ifaces.d rtables/rtable.d hosts  
* python3 station.py -no ifaces/ifaces.e rtables/rtable.e hosts

## Commands

### Station
* ```send <destination> <message>``` - send message to a destination host
* ```show arp```		- show the ARP cache table information
* ```show pq``` 		- show the pending_queue 
* ```show host``` 		- show the IP/name mapping table
* ```show iface``` 		- show the interface information
* ```show rtable``` 	- show the contents of routing table
* ```quit```            - close the station

### Router
* ```show arp``` 		- show the ARP cache table information
* ```show pq``` 		- show the pending_queue
* ```show host``` 		- show the IP/name mapping table
* ```show iface``` 		- show the interface information
* ```show rtable``` 	- show the contents of routing table
* ```quit```            - close the router

### Bridge
* ```show sl```     - show the contents of self-learning table
* ```quit```        - close the bridge

## Note
There are several constants like timeouts defined in util.py
* BUFFER_LEN = 10240
* SL_TIMEOUT = 30 # bridge self learning table timeout in seconds
* SL_REFRESH_PERIOD = 1 # bridge self learning table thread refresh in seconds
* ARP_REFRESH_PERIOD = 1 # station arp cache thread refresh in seconds
* ARP_TIMEOUT = 30 # station arp cache table timeout in seconds

Change these as needed. If a ModuleNotFoundError is encountered use pip install to install that module.
