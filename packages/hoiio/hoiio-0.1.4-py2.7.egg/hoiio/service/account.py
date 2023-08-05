from hoiio.service import Service
from hoiio.service import api_endpoint


class Account(Service):
    """ 
    Provide account related services such as retrieve the credit balance and account information
    """
    
    def __init__(self):
        pass

    def balance(self, **kwargs):
        """
        Retrieve the credit balance
        
        :returns: Return :class:`hoiio.service.Response`
        """
        return self.make_request(api_endpoint('user', 'get_balance'), **kwargs)
       

    def info(self, **kwargs):
        """
        Retrieve account info
        
        :returns: Return :class:`hoiio.service.Response`
        """
        res = self.make_request(api_endpoint('user', 'get_info'), **kwargs)
        # To be consistent with Hoiio.number.available_countries, we remove + 
        if res.prefix.startswith('+'):
        	res.prefix = res.prefix[1:]
        return res 
       
