from unittest import TestCase
import geo
import people
import math
import text
from django_sample_data.api import *

class TestSample(TestCase):
    def test1(self):
        from mock import patch
        with patch('%s.load_data' % __name__, lambda *args: ['aaa']):
            first_name()
        with patch('%s.load_data' % __name__, lambda lang,gender: ['%s_%s'% (lang, gender)]) as load_data:
            first_name(['it'], ['m'])
            load_data.assert_called_with(None, None, None)


__test__ = {
    'geo': geo,
    'people': people,
    'math': math,
    'text': text,
}
