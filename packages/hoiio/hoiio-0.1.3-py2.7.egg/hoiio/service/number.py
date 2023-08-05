from hoiio.service import Service
from hoiio.service import api_endpoint

class Number(Service):
    """ 
    Provide Number services such as subscribing and configuring the numbers.
    """
    
    def __init__(self):
        pass

    def available_countries(self, **kwargs):
        """
        Returns the countries that have Hoiio numbers.

        :returns: Return :class:`hoiio.service.Response`
        """
        res = self.make_request(api_endpoint('number', 'get_countries'), **kwargs)
        # We make sure states attribute is None if not present 
        for country in res.entries:
            if not hasattr(country, 'states'):
                country.states = None
        return res


    def available_numbers(self, country, state=None, **kwargs):
        """
        Returns the available numbers for purchase
        
        :param country: The country with available numbers
        :param state: The state in the country. Required for countries with states.

        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['country'] = country
        if state != None:
            kwargs['state'] = state
        return self.make_request(api_endpoint('number', 'get_choices'), **kwargs)


    def rate(self, country, **kwargs):
        """
        Returns the subscription cost of the country

        :param country: Subscription cost of the country

        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['country'] = country
        return self.make_request(api_endpoint('number', 'get_rates'), **kwargs)


    def subscribe(self, number, duration, **kwargs):
        """
        Subscribe a number

        :param number: The number to subscribe to
        :param duration: The number of months to subscribe to
        :type duration: 1, 3, 12 or auto_extend

        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['number'] = number
        kwargs['duration'] = duration
        return self.make_request(api_endpoint('number', 'subscribe'), **kwargs)

    # Not useful since API will override
    # def configure_voice(self, number, notify_url, **kwargs):
    #   """
    #   Configure the Notify URL of a number for voice call. The Notify URL is needed for Hoiio to post notification to your server when a call is received at the number.
    #   """
    #   return self.configure(number, mode='voice', forward_to=notify_url)

    # def configure_fax(self, number, notify_url, **kwargs):
    #   """
    #   Configure the Notify URL of a number for fax. The Notify URL is needed for Hoiio to post notification to your server when a fax is received at the number.
    #   """
    #   return self.configure(number, mode='fax', forward_to=notify_url)

    # def configure_sms(self, number, notify_url, **kwargs):
    #   """
    #   Configure the Notify URL of a number for SMS. The Notify URL is needed for Hoiio to post notification to your server when an SMS is received at the number.
    #   """
    #   return self.configure(number, forward_sms_to=notify_url)

    def configure(self, number, **kwargs):
        """
        Configure a number. It is recommended to use configure_voice, configure_fax or configure_sms instead of this.

        :param number: The number to configure
        :param forward_to: The notify_url when there is an incoming call (could be voice or fax depending on mode).
        :param forward_sms_to: The notify_url when there is an incoming SMS
        :param mode: The mode for incoming call. It can either be voice or fax (but not both). Default to voice.
        :type mode: voice or fax

        :returns: Return :class:`hoiio.service.Response`
        """
        kwargs['number'] = number
        return self.make_request(api_endpoint('number', 'update_forwarding'), **kwargs)


    def subscribed_numbers(self, **kwargs):
        """
        Retrieve the list of subscribed numbers

        :returns: Return :class:`hoiio.service.Response`
        """
        return self.make_request(api_endpoint('number', 'get_active'), **kwargs)



