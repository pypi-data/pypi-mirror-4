import urllib
import urllib2

import service.voice
import service.sms
import service.fax
import service.ivr
import service.number
import service.user

class Hoiio:

	# Services as class attributes
	voice = service.voice.Voice()
	# sms = service.sms.Sms()
	# fax = service.fax.Fax()
	# ivr = service.ivr.Ivr()
	# number = service.number.Number()
	# user = service.user.User()

	@staticmethod
	def test_call():
		print 'calling from class Hoiio..'
		return True

# url = 'http://www.acme.com/users/details'
# params = urllib.urlencode({
#   'firstName': 'John',
#   'lastName': 'Doe'
# })
# response = urllib2.urlopen(url, params).read()














