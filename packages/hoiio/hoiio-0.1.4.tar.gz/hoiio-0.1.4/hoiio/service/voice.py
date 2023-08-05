from hoiio.service import Service

from hoiio.service import api_endpoint


class Voice(Service):
    """ 
    Provide voice services such as making a call back, conference call, and query for calls. 

    Usage: Hoiio.voice.call(...), Hoiio.voice.conference(...), etc.
    """
    
    def __init__(self):
        pass

    def call(self, dest1, dest2, **kwargs):
        """
        Call 2 phone numbers and connect them up

        :param dest1: The first phone number to call. If None, Hoiio will call the account's registered mobile number. 
        :param dest2: The second phont number to call
        :param caller_id: The caller ID to show to :data:`dest2`
        :param max_duration: Maximum duration (in seconds). Call will be hangup after :data:`max_duration`
        
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Calling %s to %s' % (dest1, dest2)
        kwargs['dest1'] = dest1
        kwargs['dest2'] = dest2
        return self.make_request(api_endpoint('voice', 'call'), **kwargs)
        

    def conference(self, *dests, **kwargs):
        """
        Call multiple phone numbers and connect them up in a conference call

        :param dests: List of phone numbers to call
        
        :param string room: The conference room to transfer the callers to
        :param caller_id: The caller ID to show to :data:`dest2`
        
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Conference call to %s' % (dests,)
        kwargs['dest'] = ','.join(dests)
        return self.make_request(api_endpoint('voice', 'conference'), **kwargs)


    def hangup(self, txn_ref, **kwargs):
        """
        Hangup a call. For conference, you need to hangup for each of the participants.

        :param txn_ref: The transaction reference for the call to hangup

        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Hangup %s' % (txn_ref)
        kwargs['txn_ref'] = txn_ref
        return self.make_request(api_endpoint('voice', 'hangup'), **kwargs)


    def history(self, **kwargs):
        """
        Retrieve the history of calls. There is pagination, and each page returns up to 100 entries.

        :param string from: Calls made after this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param string to: Calls made before this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param int page: The page number. Count starts from 1.
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Call history'
        return self.make_request(api_endpoint('voice', 'get_history'), **kwargs)


    def rate(self, dest1, dest2, **kwargs):
        """
        Retrieve the cost of making a call

        :param dest1: The first phone number to call. 
        :param dest2: The second phont number to call
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Calling %s to %s' % (dest1, dest2)
        kwargs['dest1'] = dest1
        kwargs['dest2'] = dest2
        return self.make_request(api_endpoint('voice', 'get_rate'), **kwargs)


    def status(self, txn_ref, **kwargs):
        """
        Retrieve the status and various information about a call

        :param txn_ref: The transaction reference for the call
        
        :returns: Return :class:`hoiio.service.Response`
        """     
        print 'Status of %s' % (txn_ref)
        kwargs['txn_ref'] = txn_ref
        return self.make_request(api_endpoint('voice', 'query_status'), **kwargs)

