from app import calc
from django.test import SimpleTestCase


class CalcTests(SimpleTestCase):
    def test_add_number(self):
        res = calc.add(5,6)
        self.assertEquals(res, 11)   