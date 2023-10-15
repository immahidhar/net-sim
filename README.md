# net-sim
Network Simulator - Data Com project

 python3 bridge.py cs1 8
 python3 bridge.py cs2 8
 python3 bridge.py cs3 8

python3 station.py -no ifaces/ifaces.a rtables/rtable.a hosts
python3 station.py -no ifaces/ifaces.b rtables/rtable.b hosts
python3 station.py -no ifaces/ifaces.c rtables/rtable.c hosts
python3 station.py -no ifaces/ifaces.d rtables/rtable.d hosts
python3 station.py -no ifaces/ifaces.e rtables/rtable.e hosts

python3 station.py -route ifaces/ifaces.r1 rtables/rtable.r1 hosts
python3 station.py -route ifaces/ifaces.r2 rtables/rtable.r2 hosts
