from hoiio.service import Service
from hoiio.service import api_endpoint

import base64

class Fax(Service):
    """ 
    Provide Fax services such as sending and querying for Fax.

    Usage: Hoiio.fax.send(...), Hoiio.fax.history(...), etc.
    """
    
    def __init__(self):
        pass

    def send(self, dest, filename, **kwargs):
        """
        Send a fax to a fax number

        :param dest: The fax number to send fax to
        :param file: The path to the pdf file to fax
        
        :param caller_id: The caller ID when connected to the fax number
        :param filename: The filename to store on Hoiio. If omitted, the filename of the file will be used.
        :param tag: Your own reference tag for this transaction
        :param notify_url: A notification URL for Hoiio to call to your web server
        
        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Faxing [%s] to %s' % (filename, dest)
        f = open(filename, "r")
        data = f.read()
        str_data = base64.b64encode(data)

        kwargs['dest'] = dest
        kwargs['file'] = str_data
        return self.make_request(api_endpoint('fax', 'send'), **kwargs)
        

    def history(self, **kwargs):
        """
        Retrieve the history of Fax. There is pagination, and each page returns up to 100 entries.

        :param string from: Fax sent/received after this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param string to: Fax sent/received before this date. In "YYYY-MM-DD HH:MM:SS" (GMT+8) format.
        :param int page: The page number. Count starts from 1.
        :param type: The type of fax. Default to all.
        :type type: incoming, outgoing or all

        :returns: Return :class:`hoiio.service.Response`
        """
        print 'Fax history'
        return self.make_request(api_endpoint('fax', 'get_history'), **kwargs)


    def rate(self, dest, **kwargs):
        """
        Retrieve the cost of sending a fax

        :param dest: The fax number to send to
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['dest'] = dest
        return self.make_request(api_endpoint('fax', 'get_rate'), **kwargs)


    def rate_in(self, dest, **kwargs):
        """
        Retrieve the cost of receiving a fax

        :param dest: The fax number to receiving at
        
        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['incoming'] = dest
        return self.make_request(api_endpoint('fax', 'get_rate'), **kwargs)


    def status(self, txn_ref, **kwargs):
        """
        Retrieve the status and various information about a fax

        :param txn_ref: The transaction reference for the fax
        
        :returns: Return :class:`hoiio.service.Response`
        """     
        print 'Status of %s' % (txn_ref)
        kwargs['txn_ref'] = txn_ref
        return self.make_request(api_endpoint('fax', 'query_status'), **kwargs)

