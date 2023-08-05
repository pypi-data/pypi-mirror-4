from hoiio.service import Service

from hoiio.service import api_endpoint



class Sms(Service):
    """ 
    Provide SMS services such as sending and querying for SMS.

    Usage: Hoiio.sms.send(...), Hoiio.sms.history(...), etc.
    """
    
    def __init__(self):
        pass

    def send(self, msg, dest, **kwargs):
        """
        Send a SMS to a phone

        :param msg: The SMS message
        :param dest: The phone number to send SMS to
        
        :param sender_name: The sender name that will be displayed to :data:`dest`
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to SMS to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Sending [%s] to %s' % (msg, dest)
        kwargs['dest'] = dest
        kwargs['msg'] = msg
        return self.make_request(api_endpoint('sms', 'send'), **kwargs)
        

    def bulk_send(self, msg, *dests, **kwargs):
        """
        Send SMS to multiple phone numbers (up to 1,000).

        :param dests: List of phone numbers to send SMS to
        :param msg: The SMS message
        
        :param sender_name: The sender name that will be displayed to :data:`dest`
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to SMS to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Sending [%s] to %s' % (msg, dests)
        kwargs['dest'] = ','.join(dests)
        kwargs['msg'] = msg
        return self.make_request(api_endpoint('sms', 'bulk_send'), **kwargs)
        

    def history(self, **kwargs):
        """
        Retrieve the history of SMS. There is pagination, and each page returns up to 100 entries.

        :param string from: SMS sent/received after this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param string to: SMS sent/received made before this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param int page: The page number. Count starts from 1.
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'SMS history'
        return self.make_request(api_endpoint('sms', 'get_history'), **kwargs)


    def rate(self, msg, dest, **kwargs):
        """
        Retrieve the cost of sending an SMS

        :param msg: The SMS message
        :param dest: The phone number to send SMS to
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'SMS rate from %s [%s]' % (dest, msg)
        kwargs['dest'] = dest
        kwargs['msg'] = msg
        return self.make_request(api_endpoint('sms', 'get_rate'), **kwargs)

    def rate_in(self, dest, **kwargs):
        """
        Retrieve the cost of sending an SMS

        :param dest: The phone number to receive the SMS at
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'SMS rate receiving at %s' % (dest)
        kwargs['incoming'] = dest
        return self.make_request(api_endpoint('sms', 'get_rate'), **kwargs)


    def status(self, txn_ref, **kwargs):
        """
        Retrieve the status and various information about an SMS

        :param txn_ref: The transaction reference for the SMS
        
        :returns: Return :class:`hoiio.service.Response`
        """     
        print 'Status of %s' % (txn_ref)
        kwargs['txn_ref'] = txn_ref
        return self.make_request(api_endpoint('sms', 'query_status'), **kwargs)
       
