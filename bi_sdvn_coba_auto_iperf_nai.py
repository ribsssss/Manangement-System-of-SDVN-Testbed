import time
from pymongo import MongoClient
import subprocess
from datetime import datetime
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from tpda_new import tpa
from settpa import setNode
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import multiprocessing


uri = "mongodb+srv://luthfirestu05:cILcoPfhKAr0jWZa@cluster0.sr7fecp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['test']  # Replace 'your_database' with your actual database name
collection = db['simulations']  # Replace 'your_collection' with your actual collection name

# Query for the latest document and retrieve values for n and topology
latest_document = collection.find().sort('_id', -1).limit(1).next()  # Assuming _id is a timestamp field
n = latest_document['numberOfCars']
topol = latest_document['topology']
if (topol == "Bidirectional Highway 6 Plane"):
    topo = "bi"
else: 
    topo = "bi"

def run_iperf(car, id):
    with open(f'iperf_output_car{id}_client.txt', 'w') as f_iperf:
        iperf_command = f'iperf -u -c 192.168.0.1 -p 5001 -t 10'
        result = car.cmd(iperf_command)
        f_iperf.write(result)

def run_ping(car, id):
    with open(f'ping_output_car{id}_client.txt', 'w') as f_ping:
        ping_command = f'ping -c 5 192.168.0.1'
        result = car.cmd(ping_command)
        f_ping.write(result)

def topology():
    info("*** Create a Network\n")
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference, ac_method='ssf')

    info("*** Creating Nodes\n")
    for id in range(0, n):
        net.addCar('car%s' % (id+1), wlans=2)
    kwargs = {'mode': 'ax2', 'client_isolation': True, 'failMode': 'standalone'}
    e1 = net.addAccessPoint('e1', mac='00:00:00:11:00:02', channel='1', 
                            position='300,1000,0' , ssid= 'vanet-ssid1', **kwargs)
    e2 = net.addAccessPoint('e2', mac='00:00:00:11:00:03', channel='11', 
                            position='-300,1000,0', ssid= 'vanet-ssid2', **kwargs)                           
    c1 = net.addController('c1')                          

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring Nodes\n")
    net.configureNodes()
    
    info("*** Creating Links\n")    
    net.addLink(e1, e2)

    info("*** Calling Sumo\n")
    net.useExternalProgram(program=sumo, port=8813,
                           config_file='{}.sumocfg --start'.format(topo),
                           clients=1, exec_order=0)

    info("*** Starting Network\n")
    net.build()
    c1.start()
    for enb in net.aps:
        enb.start([c1])
    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))
    e1.cmd('ovs-ofctl add-flow e1 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
    e1.cmd('ovs-ofctl add-flow e1 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
    e1.cmd('ovs-ofctl add-flow e1 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
    e1.cmd('ovs-ofctl add-flow e1 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')
    e2.cmd('ovs-ofctl add-flow e2 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
    e2.cmd('ovs-ofctl add-flow e2 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
    e2.cmd('ovs-ofctl add-flow e2 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
    e2.cmd('ovs-ofctl add-flow e2 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

    "Track The Position of The Nodes"
    nodes = net.cars + net.aps

    TxPower = tpa()
    for car in net.cars:
        car.setTxPower(TxPower, intf=car.wintfs[0])

    net.telemetry(nodes=nodes, single=True, data_type='rssi',
                  min_x=-1000, min_y=500,
                  max_x=1000, max_y=1500)

    info("*** Running Iperf and Ping\n")
    processes = []
    for id, car in enumerate(net.cars):
        p_iperf = multiprocessing.Process(target=run_iperf, args=(car, id+1))
        processes.append(p_iperf)
        p_iperf.start()
        p_ping = multiprocessing.Process(target=run_ping, args=(car, id+1))
        processes.append(p_ping)
        p_ping.start()

    for p in processes:
        p.join()


    info("*** Stopping Network\n")
    timesleep(20)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
