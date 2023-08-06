"""
Can find peers in local area networks.
"""

import cPickle as pickle
import struct
import uuid
from gevent.socket import socket


# This addr-pair is used to receive
# active multicast announcements
_PASSIVE_MCAST_GRP = '224.1.1.59'
_PASSIVE_MCAST_PORT = 51337

class Finder:
   
    def __init(self):
        # "Blacklisted" signatures
        self.ignore_uuids = set()
        self.peers = {}
    
    def _setup_passive(self):
        
        # Create a new udp socket for the passive finder
        self.socket = socket(socket.AF_INET,
                             socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        
        # Reuse the port
        self.socket.setsockopt(socket.SOL_SOCKET,
                               socket._SO_REUSEADDR,
                               1)
                   
    def start_passive(self):
        return gevent.spawn(find, passively_forever)
                                   
    def find_passively_forever(self):
        
        try:
            # Ensure passive mode
            _setup_passive()
        
            # Bind socket
            self.socket.bind(('0.0.0.0', _PASSIVE_MCAST_PORT))
                
            # Used to request membership
            membershipreq = struct.pack("4sl", 
                                        socket.inet_aton(_PASSIVE_MCAST_GRP),
                                        socket.INADDR_ANY)

            # Request membership
            sock.setsockopt(socket.IPPROTO_IP, 
                            socket.IP_ADD_MEMBERSHIP,
                            membershipreq)

            while True:
                # Receive datagram
                data, addr = self.socket.recvfrom(512)
                
                try:
                    # Unpickle the data
                    req = pickle.loads(data)
                    
                    # Well, this uuid should be ignored!
                    if req['header.uuid'] in self.ignore_uuids:
                        continue

                    # Save the body data
                    self.peers[addr] = req['body']
                except:
                    ### Screw bad requests
                    pass
                
        finally:
            # Close if not none
            if self.socket:
                self.socket.close()  
            
            
