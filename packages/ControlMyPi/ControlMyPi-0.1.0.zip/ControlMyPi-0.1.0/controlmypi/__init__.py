'''
Created on 20 Dec 2012

ControlMyPi.com connection module. Include this in your project and follow the
examples on controlmypi.com/help.

Requires SleekXMPP, dnspython, pyasn1 and pyasn1_modules

@version: 1

@author: Jeremy Blythe (@jerbly - jeremyblythe.blogspot.com)
'''

import sys
import sleekxmpp
import json
import logging
import threading

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8') #@UndefinedVariable
else:
    raw_input = input

APPSPOT = 'controlmypi@appspot.com/bot'

class ControlMyPiException(Exception):
    pass

class ControlMyPi(sleekxmpp.ClientXMPP):

    """
    A SleekXMPP bot that will send the control panel setup
    to controlmypi and call on_control_message when a message
    is received from controlmypi.
    """

    def __init__(self, bare_jid, password, id, friendly_name, panel_form, on_control_message, visibility='hid', on_registered=None):
        # Check that the id is Alphanumeric and max 9 characters:
        if len(id) < 1 or len(id) > 9:
            raise ControlMyPiException('Instance ID must be between 1 and 9 characters')
        if not id.isalnum():
            raise ControlMyPiException('Instance ID must only contain alphanumeric characters')
        # Check the visibility type
        if visibility not in ['pub','pri','hid']:
            raise ControlMyPiException('Unknown visibility type. Must be pub, hid or pri')
        sleekxmpp.ClientXMPP.__init__(self, bare_jid+'/'+id+'^', password)
        self.recipient = APPSPOT
        self.cp_msg = json.dumps({'register':{'ver':1, 'name':friendly_name, 'panel':panel_form, 'p_type':visibility}})
        self.on_msg = on_control_message
        self.on_reg = on_registered
        self.add_event_handler("session_start", self._start)
        self.add_event_handler("message", self._message)
        self._key = ''
        self.use_ipv6 = False
        self._status = {}
        self._active = False
        
    def _start(self, event):
        """
        Process the session_start event. Send the control_panel_message to controlmypi.
        """
        self.send_message(mto=self.recipient, mbody=self.cp_msg, mtype='chat')        

    def _message(self, msg):
        """
        Process incoming message stanzas. Check they are from controlmypi before 
        calling on_msg.
        """
        if msg['type'] in ('chat', 'normal'):
            if msg['from'] == APPSPOT:
                body = msg['body']
                if body.startswith('^key='):
                    self._key = body.split('=')[1]
                    logging.info('Registered with controlmypi.')
                    self._ping()
                    if self.on_reg is not None:
                        self.on_reg(self)
                elif body == '^start':
                    logging.debug("Start sending!")
                    self._active = True
                    self._send_status(self._status)
                elif body == '^stop':
                    logging.debug("Stop sending!")
                    self._active = False
                else:
                    m = json.loads(body)
                    if type(m) is dict:
                        k,v = m.items()[0]
                        self.on_msg(self, k, v) 

    def _ping(self):
        t = threading.Timer(1800.0, self._ping)
        t.daemon = True
        t.start()
        self.send_message(mto=self.recipient, mbody=json.dumps({'ping' : {'^key':self._key} }), mtype='chat')

    def _send_status(self, status_map):
        if self._active:
            status_map['^key'] = self._key
            self.send_message(mto=self.recipient, mbody=json.dumps({'update' : status_map}), mtype='chat')                
    
    def update_status(self, status_map):
        """
        Send a status update message to controlmypi to have status indicators updated.
        """
        # Copy the incoming map into _status
        self._status.update(status_map)        
        self._send_status(status_map)
        
    def start_control(self):
        """
        Start a non-blocking jabber connection
        """
        if self.connect():
            self.process()
            return True
        else:
            return False
        
    def stop_control(self):
        """
        Disconnect the jabber connection
        """
        self.disconnect()


