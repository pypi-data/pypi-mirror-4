__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Junda Ong'
__author_email__ = 'junda@hoiio.com'

import urllib
import urllib2

import service.voice
import service.sms
import service.fax
import service.ivr
import service.number
import service.account

class Hoiio(object):

    # Services as class attributes
    voice = service.voice.Voice()
    sms = service.sms.Sms()
    number = service.number.Number()
    fax = service.fax.Fax()
    ivr = service.ivr.Ivr()
    account = service.account.Account()

    services = [voice, sms, number, fax, ivr, account]

    @staticmethod
    def init(app_id, access_token):
        for service in Hoiio.services:
            service.set_auth(app_id, access_token)
            service._Hoiio = Hoiio

    # Phone number prefix
    _prefix = '1'

    # http://stackoverflow.com/questions/128573/using-property-on-classmethods
    class __metaclass__(type):
        @property
        def prefix(cls):
                return cls._prefix
        @prefix.setter
        def prefix(cls, value):
                if value.startswith('+'):
                    value = value[1:]
                cls._prefix = value

class CallStatus:
    """ The Call Status"""
    ANSWERED = 'answered'
    UNANSWERED = 'unanswered'
    FAILED = 'failed'
    BUSY = 'busy'
    ONGOING = 'ongoing'

class SmsStatus:
    """ The SMS Status"""
    QUEUED = 'queued'
    DELIVERED = 'delivered'
    FAILED = 'failed'
    ERROR = 'error'
    RECEIVED = 'received'

class FaxStatus:
    """ The Fax Status"""
    ANSWERED = 'answered'
    UNANSWERED = 'unanswered'
    FAILED = 'failed'
    BUSY = 'busy'
    ONGOING = 'ongoing'


