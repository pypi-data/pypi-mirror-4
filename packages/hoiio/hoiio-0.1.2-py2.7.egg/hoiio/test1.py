import unittest

from hoiio.api import Hoiio

APP_ID = 'Kej4yXQvnVDUzDmH'
ACCESS_TOKEN = 'A7Q88c2UehAAfncP'

Hoiio.init(APP_ID, ACCESS_TOKEN)

# Makes a voice call back
Hoiio.call('+6591378000', '+6566028066')

