class setNode():
    def __init__(self, name):
        super().__init__(name)
        self.txPower = None

    def setTxPower(self, txPower):
        self.cmd('iw dev {} set txPower fixed {}'.format(self.iface, txPower))
        self.txPower = txPower

    def getTxPower(self):
        return self.txPower if self.txPower is not None else 0
