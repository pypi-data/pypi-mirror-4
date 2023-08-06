from django.db import models
from django.core.exceptions import ValidationError
from unittest import TestCase

import datetime

from .forms import TimedeltaFormField
from .fields import TimedeltaField
from .widgets import TimedeltaWidget
from .helpers import *

class TimedeltaWidgetTest(TestCase):
    def test_render(self):
        """
        >>> t = TimedeltaWidget()
        >>> t.render('', datetime.timedelta(days=1), {})
        u'<input type="text" name="" value="1 day" />'
        >>> t.render('', datetime.timedelta(days=0), {})
        u'<input type="text" name="" />'
        >>> t.render('', datetime.timedelta(seconds=1), {})
        u'<input type="text" name="" value="1 second" />'
        >>> t.render('', datetime.timedelta(seconds=10), {})
        u'<input type="text" name="" value="10 seconds" />'
        >>> t.render('', datetime.timedelta(seconds=30), {})
        u'<input type="text" name="" value="30 seconds" />'
        >>> t.render('', datetime.timedelta(seconds=60), {})
        u'<input type="text" name="" value="1 minute" />'
        >>> t.render('', datetime.timedelta(seconds=150), {})
        u'<input type="text" name="" value="2 minutes, 30 seconds" />'
        >>> t.render('', datetime.timedelta(seconds=1800), {})
        u'<input type="text" name="" value="30 minutes" />'
        >>> t.render('', datetime.timedelta(seconds=3600), {})
        u'<input type="text" name="" value="1 hour" />'
        >>> t.render('', datetime.timedelta(seconds=3601), {})
        u'<input type="text" name="" value="1 hour, 1 second" />'
        >>> t.render('', datetime.timedelta(seconds=19800), {})
        u'<input type="text" name="" value="5 hours, 30 minutes" />'
        >>> t.render('', datetime.timedelta(seconds=91800), {})
        u'<input type="text" name="" value="1 day, 1 hour, 30 minutes" />'
        >>> t.render('', datetime.timedelta(seconds=302400), {})
        u'<input type="text" name="" value="3 days, 12 hours" />'
        """

class MinMaxTestModel(models.Model):
    min = TimedeltaField(min_value=datetime.timedelta(1))
    max = TimedeltaField(max_value=datetime.timedelta(1))
    minmax = TimedeltaField(min_value=datetime.timedelta(1), max_value=datetime.timedelta(7))
    
class TimedeltaModelFieldTest(TestCase):
    def test_validate(self):
        test = MinMaxTestModel(
            min=datetime.timedelta(1),
            max=datetime.timedelta(1),
            minmax=datetime.timedelta(1)
        )
        test.full_clean() # This should have met validation requirements.
        
        test.min = datetime.timedelta(hours=23)
        self.assertRaises(ValidationError, test.full_clean)
        
        test.min = datetime.timedelta(hours=25)
        test.full_clean()
        
        test.max = datetime.timedelta(11)
        self.assertRaises(ValidationError, test.full_clean)
        
        test.max = datetime.timedelta(hours=20)
        test.full_clean()
        
        test.minmax = datetime.timedelta(0)
        self.assertRaises(ValidationError, test.full_clean)
        test.minmax = datetime.timedelta(22)
        self.assertRaises(ValidationError, test.full_clean)
        test.minmax = datetime.timedelta(6, hours=23, minutes=59, seconds=59)
        test.full_clean()

class TimedeltaFormFieldTest(TestCase):
    def test_clean(self):
        """
        >>> t = TimedeltaFormField()
        >>> t.clean('1 day')
        datetime.timedelta(1)
        >>> t.clean('1 day, 0:00:00')
        datetime.timedelta(1)
        >>> t.clean('1 day, 8:42:42.342')
        datetime.timedelta(1, 31362, 342000)
        >>> t.clean('3 days, 8:42:42.342161')
        datetime.timedelta(3, 31362, 342161)
        >>> t.clean('3 days, 8:42:42.3.42161')
        Traceback (most recent call last):
        ValidationError: [u'Enter a valid time span: e.g. "3 days, 4 hours, 2 minutes"']
        >>> t.clean('5 day, 8:42:42')
        datetime.timedelta(5, 31362)
        >>> t.clean('1 days')
        datetime.timedelta(1)
        >>> t.clean('1 second')
        datetime.timedelta(0, 1)
        >>> t.clean('1 sec')
        datetime.timedelta(0, 1)
        >>> t.clean('10 seconds')
        datetime.timedelta(0, 10)
        >>> t.clean('30 seconds')
        datetime.timedelta(0, 30)
        >>> t.clean('1 minute, 30 seconds')
        datetime.timedelta(0, 90)
        >>> t.clean('2.5 minutes')
        datetime.timedelta(0, 150)
        >>> t.clean('2 minutes, 30 seconds')
        datetime.timedelta(0, 150)
        >>> t.clean('.5 hours')
        datetime.timedelta(0, 1800)
        >>> t.clean('30 minutes')
        datetime.timedelta(0, 1800)
        >>> t.clean('1 hour')
        datetime.timedelta(0, 3600)
        >>> t.clean('5.5 hours')
        datetime.timedelta(0, 19800)
        >>> t.clean('1 day, 1 hour, 30 mins')
        datetime.timedelta(1, 5400)
        >>> t.clean('8 min')
        datetime.timedelta(0, 480)
        >>> t.clean('3 days, 12 hours')
        datetime.timedelta(3, 43200)
        >>> t.clean('3.5 day')
        datetime.timedelta(3, 43200)
        >>> t.clean('1 week')
        datetime.timedelta(7)
        >>> t.clean('2 weeks, 2 days')
        datetime.timedelta(16)
        >>> t.clean(u'2 we\xe8k, 2 days')
        Traceback (most recent call last):
        ValidationError: [u'Enter a valid time span: e.g. "3 days, 4 hours, 2 minutes"']
        """
    

class TimedeltaHelpersTest(TestCase):
    def test_parse(self):
        """
        >>> parse('1 day')
        datetime.timedelta(1)
        >>> parse('2 days')
        datetime.timedelta(2)
        >>> parse("1.5 days")
        datetime.timedelta(1, 43200)
        >>> parse("3 weeks")
        datetime.timedelta(21)
        >>> parse("4.2 hours")
        datetime.timedelta(0, 15120)
        >>> parse(".5 hours")
        datetime.timedelta(0, 1800)
        >>> parse(" hours")
        Traceback (most recent call last):
            ...
        TypeError: ' hours' is not a valid time interval
        >>> parse("1 hour, 5 mins")
        datetime.timedelta(0, 3900)
        """
    
    def test_multiply(self):
        """
        >>> multiply(datetime.timedelta(1), 2.5)
        datetime.timedelta(2, 43200)
        >>> multiply(datetime.timedelta(1), 3)
        datetime.timedelta(3)
        >>> multiply(datetime.timedelta(1), Decimal("5.5"))
        datetime.timedelta(5, 43200)
        >>> multiply(datetime.date.today(), 2.5)
        Traceback (most recent call last):
            ...
        AssertionError: First argument must be a timedelta.
        >>> multiply(datetime.timedelta(1), "2")
        Traceback (most recent call last):
            ...
        AssertionError: Second argument must be a number.
        """
    def test_divide(self):
        """
        >>> divide(datetime.timedelta(1), datetime.timedelta(hours=6))
        4
        >>> divide(datetime.timedelta(2), datetime.timedelta(3))
        0
        >>> divide(datetime.timedelta(8), datetime.timedelta(3), as_float=True)
        2.6666666666666665
        >>> divide(datetime.timedelta(8), 2.0)
        datetime.timedelta(4)
        >>> divide(datetime.timedelta(8), 2, as_float=True)
        Traceback (most recent call last):
            ...
        AssertionError: as_float=True is inappropriate when dividing timedelta by a number.
        """
    
    def test_percentage(self):
        """
        >>> percentage(datetime.timedelta(4), datetime.timedelta(2))
        200.0
        >>> percentage(datetime.timedelta(2), datetime.timedelta(4))
        50.0
        
        """
    
    def test_decimal_percentage(self):
        """
        >>> decimal_percentage(datetime.timedelta(4), datetime.timedelta(2))
        Decimal('200.0')
        >>> decimal_percentage(datetime.timedelta(2), datetime.timedelta(4))
        Decimal('50.0')
        
        """
    
    
    def test_round_to_nearest(self):
        """
        >>> td = datetime.timedelta(minutes=30)
        >>> round_to_nearest(datetime.timedelta(minutes=0), td)
        datetime.timedelta(0)
        >>> round_to_nearest(datetime.timedelta(minutes=14), td)
        datetime.timedelta(0)
        >>> round_to_nearest(datetime.timedelta(minutes=15), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(minutes=29), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(minutes=30), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(minutes=42), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(hours=7, minutes=22), td)
        datetime.timedelta(0, 27000)
        
        >>> td = datetime.timedelta(minutes=15)
        >>> round_to_nearest(datetime.timedelta(minutes=0), td)
        datetime.timedelta(0)
        >>> round_to_nearest(datetime.timedelta(minutes=14), td)
        datetime.timedelta(0, 900)
        >>> round_to_nearest(datetime.timedelta(minutes=15), td)
        datetime.timedelta(0, 900)
        >>> round_to_nearest(datetime.timedelta(minutes=29), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(minutes=30), td)
        datetime.timedelta(0, 1800)
        >>> round_to_nearest(datetime.timedelta(minutes=42), td)
        datetime.timedelta(0, 2700)
        >>> round_to_nearest(datetime.timedelta(hours=7, minutes=22), td)
        datetime.timedelta(0, 26100)

        >>> td = datetime.timedelta(minutes=30)
        >>> round_to_nearest(datetime.datetime(2010,1,1,9,22), td)
        datetime.datetime(2010, 1, 1, 9, 30)
        >>> round_to_nearest(datetime.datetime(2010,1,1,9,32), td)
        datetime.datetime(2010, 1, 1, 9, 30)
        >>> round_to_nearest(datetime.datetime(2010,1,1,9,42), td)
        datetime.datetime(2010, 1, 1, 9, 30)

        >>> round_to_nearest(datetime.time(0,20), td)
        datetime.time(0, 30)
        
        TODO: test with tzinfo (non-naive) datetimes/times.
        """
    
    def test_decimal_hours(self):
        """
        >>> decimal_hours(datetime.timedelta(hours=5, minutes=30))
        Decimal('5.5')
        >>> decimal_hours(datetime.timedelta(hours=5))
        Decimal('5')
        >>> decimal_hours(datetime.timedelta(hours=9, minutes=20))
        Decimal('9.333333333333333333333333333')
        """
