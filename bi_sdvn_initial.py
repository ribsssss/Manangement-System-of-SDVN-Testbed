#!/usr/bin/env python

"""Sample file for VANET

***Requirements***:
Kernel version: 5.8+ (due to the 802.11p support)
sumo 1.5.0 or higher
sumo-gui

Please consider reading https://mininet-wifi.github.io/80211p/ for 802.11p support
"""

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def topology():

    info("*** Create a Network\n")
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating Nodes\n")
    for id in range(0, 20):
        net.addCar('car%s' % (id+1), wlans=2, bgscan_threshold=-60,
                   s_inverval=1, l_interval=2, bgscan_module="simple")
    kwargs = {'ssid': 'vanet-ssid', 'mode': 'ax2', 'passwd': '123456789a', 'encrypt': 'wpa2',
              'failMode': 'standalone', 'datapath': 'user'}
    e1 = net.addAccessPoint('e1', mac='00:00:00:11:00:01', channel='1',
                            position='0,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)
    e2 = net.addAccessPoint('e2', mac='00:00:00:11:00:02', channel='6',
                            position='150,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)
    e3 = net.addAccessPoint('e3', mac='00:00:00:11:00:03', channel='6',
                            position='-150,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)
    e4 = net.addAccessPoint('e4', mac='00:00:00:11:00:04', channel='11',
                            position='300,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)
    e5 = net.addAccessPoint('e5', mac='00:00:00:11:00:05', channel='11',
                            position='-300,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)
    e6 = net.addAccessPoint('e6', mac='00:00:00:11:00:06', channel='1',
                            position='450,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs) 
    e7 = net.addAccessPoint('e7', mac='00:00:00:11:00:07', channel='1',
                            position='-450,1000,0', ieee80211r='yes', mobility_domain='a1b2', **kwargs)                             
    c1 = net.addController('c1')                          

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring Nodes\n")
    net.configureNodes()
    
    info("*** Creating Links\n")    
    net.addLink(e1, e2)
    net.addLink(e2, e3)
    net.addLink(e3, e4)
    net.addLink(e4, e5)
    net.addLink(e5, e6)
    net.addLink(e6, e7)

    info("*** Calling Sumo\n")
    # exec_order: Tells TraCI to give the current
    # client the given position in the execution order.
    # We may have to change it from 0 to 1 if we want to
    # load/reload the current simulation from a 2nd client
    net.useExternalProgram(program=sumo, port=8813,
                           config_file='bi.sumocfg',
                           clients=1, exec_order=0)

    info("*** Starting Network\n")
    net.build()
    for enb in net.aps:
        enb.start([c1])
    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))
                  
    "Track The Position of The Nodes"
    nodes = net.cars + net.aps
    net.telemetry(nodes=nodes, data_type='position',
                  min_x=-1000, min_y=500,
                  max_x=1000, max_y=1500)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping Network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
