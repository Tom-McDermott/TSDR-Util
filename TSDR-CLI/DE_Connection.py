# TangerineSDR Data Engine connection object.

# Author: Thomas C. McDermott, N5EG
# Copyright 2021, Thomas C. McDermott, N5EG
# License: Gnu Public License (GPL) Version 2 or (at your choice) any later Version.

# In the future there may be more than one TSDR Data Engine on the LAN.

# Modified to use some of the ASCII human-readable commands

import atexit
import binascii
import socket
import subprocess
import time
from exceptions import *
#import struct
#from typing import ByteString

class DE_LH:
    def __init__(self, TargetIP):
        
        atexit.register(self.cleanup)

        self.OurIP = subprocess.getoutput("hostname -I").split(' ', -1)[0]   # get only first IP address returned

        if TargetIP == '':      # if no target specified, broadcast on LAN/24
            TargetIP = self.OurIP[0:self.OurIP.rfind('.')+1]+'255'

        print("Discovery: Target IP address = ", TargetIP, "   Our host IP address = ", self.OurIP)

        if self.Discover(TargetIP):
            #self.CreateCnfgChan()   #   Create Configuration Channel
            #   Create other channels?
            return

        else:                               # discovery failed - raise an exception
            self.CnfgChan = None
            raise(DiscoveryFail("Data Engine not found"))


    # def __enter__(self):
    #     pass

    # def __exit__(self, exception_type, exception_value, traceback):

    #     print("DE_LE __exit__")
    #     if self.ProvChan:
    #         self.ProvChan[0].close()
    #     if self.CnfgChan:
    #         self.CnfgChan[0].close()



    def Discover(self, TargetIP):           # Use HPSDR Discovery to find target Data Engine, create self.ProvChan

        Discovery_Port = 1024 
        HPSDR_discovery_req = bytes(b'\xEF\xFE\x02' + 60 * b'\x00') # for Hermes.  May change for DE

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.settimeout(3.0)		# wait max 1.0 seconds on receive

        sock.sendto(HPSDR_discovery_req, (TargetIP, Discovery_Port))   # this implicitly binds our IP and our source port for receiving
        PortA = sock.getsockname()[1]                             # our UDP source port number

        try:
            data, addr = sock.recvfrom(1500)
            print("Discovery response: ", binascii.hexlify(data), addr) 

            print("Parsed Response: ", data[0:3], "  MAC : ", binascii.hexlify(data[3:9]), "  Code_ver: ", data[9],
            "  Board_ID: ", data[10], "  bytes 11-12: ", int.from_bytes(data[11:13], byteorder='big'))

            PortB = addr[1]
            print("PortA: ", PortA, "Our IP: ", self.OurIP)
            print("PortB: ", PortB, "Their IP: ", addr[0])
  
            self.TargetIP = addr[0]
            self.ProvChan = (sock, addr[0], PortB, self.OurIP, PortA)

            time.sleep(2)
            return self.ProvChan
  
        except socket.timeout:
            print("Discovery response timeout")
            sock.close()
            self.ProvChan = None
            self.CnfgChan = None
            return None
            

    def CreateCnfgChan(self):       # Configuration channel

        CreateOK = 'OK'
        CreateAck = 'AK'

        PortF = 56789           # we will need to actually create a socket to get portF
                                # this is just a placeholder for testing]
        PortC = 54321

        # CCReq = struct.pack('ccHH', b'C', b'C', PortC, PortF)    #create Confg chan request structure compatible with C

        CCReq = bytes("CC " + "1 " + str(PortC) + " " + str(PortF), 'utf-8')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PortC))

        sock.settimeout(3.0)		# wait max 1.0 seconds on receive

        Target = (self.ProvChan[1], self.ProvChan[2])   # send to the DE Provisioning Channel

        sock.sendto(CCReq, (Target))     # this implicitly binds our IP and our source port for receiving ???
                                         # maybe it doesn't implicitly bind if already bound ???

        try:
            data, addr = self.ProvChan[0].recvfrom(1500)    # the CC answer comes back on the provisioning channel
            data = str(data, 'utf-8')
            data = data.rstrip(' \t\r\n\0')                 # remove trailing whitespace

            print("Response to CC from Provisioning channel:", data)

            CmdResp = data.split(' ', 10)
            if (CmdResp[0] == CreateOK) or (CmdResp[0] == CreateAck):
                Channum = CmdResp[1]        # TODO - we don't yet know what to do with this
                PortD = int(CmdResp[2])
                PortE = int(CmdResp[3])     # TODO - we don't yet know what to do with this
                self.CnfgChan = (sock, Target[0], PortD, self.OurIP, PortC)
                print("Successful Configuration Channel creation")
            else:
                print("Configuration Channel invalid DE response: ", data)
                self.CnfgChan = None
 
        except socket.timeout:
            print("Configuration Channel Setup failed: response timeout")
            sock.close()
            self.CnfgChan = None

        finally:
            return self.CnfgChan


    def SendChan(self, channel, command):
        # Send a command on the  channel
        Cmd = bytes(command, 'utf-8')
        Target = (channel[1], channel[2])     
        channel[0].sendto(Cmd, Target)
        return

    def RecvChan(self, channel):
        # Receive a response on the  channel        
        print("Recv connection being used: ", channel)   # DEBUG
        
        try:
            data, addr = channel[0].recvfrom(1500)
            return str(data, 'utf-8')

        except socket.timeout:
            print("Channel read request: response timeout")
            return('')


    def cleanup(self):              # close sockets when done
        if self.ProvChan:
            self.ProvChan[0].close()
        if self.CnfgChan:
            self.CnfgChan[0].close()


 
