from hoiio.service import Service
from hoiio.service import api_endpoint

class Ivr(Service):
    """ 
    Provide IVR services such as Dial, Gather, Transfer, Hangup, etc.
    """
    
    def __init__(self):
        pass

    def dial(self, dest, **kwargs):
        """
        Make a call out to a phone number

        :param dest: The phone number to call to
        
        :param msg: The message to play when the phone is answered
        :param caller_id: The caller ID when connected to the phone number
        :param max_duration: The maximum duration for the call, afterwhich it will hangup automatically
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['dest'] = dest
        return self.make_request(api_endpoint('ivr/start', 'dial'), **kwargs)


    def play(self, session, msg, **kwargs):
        """
        Play a message over the phone call

        :param session: The IVR session
        :param msg: The message to play

        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        kwargs['msg'] = msg
        return self.make_request(api_endpoint('ivr/middle', 'play'), **kwargs)
                

    def gather(self, session, **kwargs):
        """
        Gather a keypad response from the user on the phone

        :param session: The IVR session
        
        :param msg: The message to play as you gather 
        :param max_digits: The maximum number of digits to gather from
        :param timeout: The call will hangup if no response after timeout (in seconds)
        :param attempts: The number of times the message will be repeated
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        return self.make_request(api_endpoint('ivr/middle', 'gather'), **kwargs)
        

    def record(self, session, **kwargs):
        """
        Record a voice message

        :param session: The IVR session
        
        :param msg: The message to play before you record
        :param max_duration: The maximum duration (in seconds) for the recorded voice message
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        return self.make_request(api_endpoint('ivr/middle', 'record'), **kwargs)

    def monitor(self, session, **kwargs):
        """
        Record the whole phone conversation from this point onwards

        :param session: The IVR session
        
        :param msg: The message to play as you record
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        return self.make_request(api_endpoint('ivr/middle', 'monitor'), **kwargs)


    def transfer(self, session, dest, **kwargs):
        """
        Transfer the call to another phone number or a conference room

        :param session: The IVR session
        :param dest: The phone number or conference room. If you are transferring to a conference room, prefix with a room: eg. room:R1234.
        
        :param msg: The message to play as you record
        :param caller_id: The caller ID when connected to the dest
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        kwargs['dest'] = dest
        return self.make_request(api_endpoint('ivr/end', 'transfer'), **kwargs)

    def hangup(self, session, **kwargs):
        """
        Hangup a phone call

        :param session: The IVR session
        
        :param msg: The message to play before you hangup
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['session'] = session
        return self.make_request(api_endpoint('ivr/end', 'hangup'), **kwargs)



