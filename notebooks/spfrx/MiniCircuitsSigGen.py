# -*- coding: utf-8 -*-
#
import telnetlib as tnet

class MCSSG(object):

    Ver = 'V1'
    ONOFF = {True: b'ON', False: b'OFF'}    
    
    def __init__(self):
        self.state = None
        
    def open(self, host, port=23, timeout=1):
        self.host    = host
        self.port    = port
        self.timeout = timeout

        if self.state != 'open':

            try:
                tn = tnet.Telnet(host, port)
            except Exception as e:
                raise Exception('Cannot open port to Mini Circuits SSG at %s:%s -- %s.' %(host, port, e))

            self.state = 'open'
            self.tn = tn
            # after open attenuator returns \r\n                
            self.read()
            return self.tn

            
    def close(self):

        if self.state == 'open':
            try:
                self.tn.close()
            except Exception as e:
                raise Exception("Cannot close port to Mini Circuits SSG at %s:%s -- %s." %(self.host, self.port, e))

            self.state = 'closed'
            del self.tn

    
    def read(self):
        try:
            strVal = self.tn.read_until(b'\n', timeout = self.timeout)
        except Exception as e:
            raise Exception("Read from Mini Circuits SSG at %s:%s failed -- %s." %(self.host, self.port, e))

        return strVal.strip(b'\r\n')


    def write(self, strCmd: str):
        try:
            strVal = self.tn.write(strCmd, timeout = self.timeout)
        except:
            raise Exception("Write to Mini Circuits SSG at %s:%s failed: %s." %(self.host, self.port, e))

        return strVal.strip(b'\r\n')


    def setFrequency(self, FreqValFloat: float):
        self.tn.write(b':FREQ:%f MHz\n' % (FreqValFloat/1e6))
        if int(self.read()) != 1:
            raise Exception("Bad response when setting Mini Circuits SSG.")


    def getFrequency(self):
        self.tn.write(b':FREQ?\n')
        return(float(self.read().split(b' ')[0]) * 1e6)

            
    def setPowerdBm(self, PwrValFloat: float):
        self.tn.write(b':PWR:%f\n' % (PwrValFloat))
        if int(self.read()) != 1:
            raise Exception("Bad response when setting Mini Circuits SSG.")


    def getPowerdBm(self):
        self.tn.write(b':PWR?\n')
        return(float(self.read()))


    def enableOutput(self, en: bool):
        self.tn.write(b':PWR:RF:%s\n' %(self.ONOFF[en]))
        if int(self.read()) != 1:
            raise Exception("Bad response when setting Mini Circuits SSG.")

            
    def __del__(self):
        self.close()

if __name__ == '__main__':

    gen = MCSSG()

    for k in range(1, 2223):
        gen.open('192.168.74.2')
        gen.setFrequency(3.96e9 + 1800*k)
        print(gen.getFrequency())
        gen.setPowerdBm(10)
        print(gen.getPowerdBm())
        gen.enableOutput(True)
        gen.close()
