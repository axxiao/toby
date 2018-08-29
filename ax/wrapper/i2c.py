"""
The connector for i2c
__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2017-04-22"
__version__ = "0.5"
"""
import smbus


class connector_i2c():
    '''
        The standard I2c connector implementation
    '''

    def __init__(self, bus_num):
        '''
            bus_num: i2c bus number, start from 0
        '''
        self.bus_num = bus_num
        self.bus = smbus.SMBus(bus_num)

    def send(self, addr, instr, reg=0x00, mode='string'):
        '''
            send string command to address

            addr: the address
            in_str: the string to be sent
        '''
        if mode == 'string':
            for ec in instr.encode(encoding='UTF-8'):
                self.bus.write_byte_data(addr, reg, ec)
        else:
            self.bus.write_byte_data(addr, reg, instr)

    def read_bytes(self, addr, length, offset=0):
        return self.bus.read_i2c_block_data(addr, offset, length)

    def receive(self, addr):
        '''
            Receive string from address

            * if no new incoming message, it will repeat the last received!
        '''
        recv = self.bus.read_i2c_block_data(addr, 0);
        rtn = ''
        for ec in recv:
            if ec < 255:
                rtn += chr(ec)
        return rtn


class tuobi_i2c():
    '''
        The I2c connector implementation for tuobi
    '''

    def __init__(self, i2c_bus_num):
        self.i2c_bus_num = i2c_bus_num
        self.i2c = connector_i2c(i2c_bus_num)
        self.last_ts = dict()

    def send(self, addr, instr, reg=0x00):
        '''
            send string command to address

            addr: the address
            in_str: the string to be sent
        '''
        if instr[-1] != ';': instr = instr + ';'
        self.i2c.send(addr, instr, reg)

    def get(self, addr):
        '''
            Receive the string from address

            return: cmd, data

            Note: different from standard i2c wrapper, it will NOT repeat the last one
        '''
        if addr not in self.last_ts: self.last_ts[addr] = -1
        recv = self.i2c.receive(addr)
        rtn = None, None
        if recv[-1] == ';':
            cmd, data, ts = recv[:-1].split(':')
            if self.last_ts[addr] < int(ts):
                # if newly received
                rtn = cmd, data
                self.last_ts[addr] = int(ts)
        return rtn