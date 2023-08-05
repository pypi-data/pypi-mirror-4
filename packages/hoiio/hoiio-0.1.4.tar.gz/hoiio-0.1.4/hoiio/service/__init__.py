import requests
import datetime

from hoiio.exceptions import HoiioException

HOIIO_API_ENDPOINT = 'https://secure.hoiio.com/open/'


class Service(object):

    # Refers back to Hoiio
    _Hoiio = None

    def __init__(self, app_id, access_token):
        setAuth(app_id, access_token)

    def set_auth(self, app_id, access_token):   
        self.app_id = app_id
        self.access_token = access_token

    def make_request(self, url, **kwargs):
        self.validate_auth()

        kwargs['app_id'] = self.app_id
        kwargs['access_token']  = self.access_token
        for key in kwargs:
            print '%s: %s' % (key, kwargs[key])

        # We add prefix if missing
        if 'dest' in kwargs:
            kwargs['dest'] = self.e164_format(kwargs['dest'])

        r = requests.get(url, params=kwargs)
        # print 'Response: %s' % r.text
        
        return Response(r)

    def validate_auth(self):
        if not hasattr(self, 'app_id') or not hasattr(self, 'access_token') or (self.app_id == None) or (self.access_token == None):
            raise HoiioException('App ID and Access Token not init')

    def e164_format(self, phone):
        if not phone.startswith('+'):
            phone = '+' + _Hoiio.prefix + phone
        return phone


class Response:
    """
    A class to encapsulate the API response. It also contains the Response class
    from requests.

    response = Response(r)
    response.status
    """

    def __init__(self, response):
        """
        response is from Requests
        """
        self.response = response
        self.json = response.json
        self.text = response.text
        try:
            for key in response.json:
                value = response.json[key]
                setattr(self, key, sanitize(key, value))

        except Exception, e:
            # It is possible that json is empty and throws: TypeError: 'NoneType' object is not iterable
            print 'Exception: %s' % e
            import traceback
            traceback.print_exc()
            raise HoiioException

    def is_success(self):
        if self.json['status'] == 'success_ok':
            return True
        return False





def api_endpoint(*args):
    """ Returns the Hoiio API endpoint URL. The args are joined by '/'. """
    endpoint = HOIIO_API_ENDPOINT + '/'.join(args)
    return endpoint
    

def sanitize(key, value):
    """ Return a value (type str) in the correct type (int, float, datetime or str) """
    
    # We do special handling for response keys
    # list (str was delimited by commas)
    if key == 'txn_refs':
        return value.split(',')
    
    # datetime
    elif key in ('date', 'expiry'):
        return str_to_date(value, key=key)

    # int
    elif key in ('split_count', 'duration', 'talktime', 'entries_count', 'total_entries_count'):
        return int(value)

    # float
    elif key in ('rate', 'total_cost', 'debit', 'balance', 'points', 'bonus'):
        return float(value)

    # bool
    elif key in ('auto_extend_status',):
        if value == 'disabled':
            return True
        else:
            return False

    # list of objects
    elif key == 'entries':
        # Turns each entry (a dict) into an object
        i = 0
        for entry in value:
            obj = obj_dic(entry)
            value[i] = obj
            i += 1
        return value

    else:
        return value


# http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
# Specially for Hoiio: Added sanitize
def obj_dic(d):
    top = type('new', (object,), d)
    seqs = tuple, list, set, frozenset
    for i, j in d.items():
        if isinstance(j, dict):
            setattr(top, i, obj_dic(j))
        elif isinstance(j, seqs):
            setattr(top, i, 
                    type(j)(obj_dic(sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(top, i, sanitize(i, j))
    return top




# Util methods
# Maybe move to hoiio module, or utils.py
def str_to_date(s, key=None):
    """ Converts a string (Hoiio format) to datetime """
    # Due to a bug from API, date might have micro sec (after .)
    if key == 'expiry':
        f = "%Y-%m-%d"
    elif '.' in s:
        f = "%Y-%m-%d %H:%M:%S.%f"
    else:
        f = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(s, f)

def date_to_str(d):
    """ Converts a datetime to string (Hoiio format) """
    # Due to a bug from API, date might have micro sec (after .)
    f = "%Y-%m-%d %H:%M:%S"
    return d.strftime(f)
