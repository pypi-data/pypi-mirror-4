import unittest
import numpy

from ibidas.utils import util
from ibidas import *


class TestCasts(unittest.TestCase):
    def test_rep(self):
        x = Rep((['hoi',2,3],['dag','dag','dag'],[set([1,2,Missing]),set([1,2,3]),set([4,5,6])],['1',Missing,'3'],['4','5','6']),allow_convert=True)
        str(x.f3 + 3)
        str(x.f4 + 4)
