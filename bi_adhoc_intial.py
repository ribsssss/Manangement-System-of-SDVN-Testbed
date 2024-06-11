from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd, mesh
from mn_wifi.wmediumdConnector import interference


def topology():
    info("*** Create a Network\n")
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating Nodes\n")
    for id in range(0, 20):
        net.addCar('car%s' % (id+1), wlans=2)                       

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring Nodes\n")
    net.configureNodes()
    
    info("*** Creating Links\n")    
    for car in net.cars:
        net.addLink(car, intf=car.params['wlan'][0], mode='ax2',
                    cls=mesh, ssid='mesh-ssid', channel=5, ht_cap='HT40+')

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
    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))
                  
    "Track The Position of The Nodes"
    nodes = net.cars
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
