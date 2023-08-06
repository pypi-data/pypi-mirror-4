"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.timezone import now
from monsieur.models import Tag, DataPoint, DataAttribute
import monsieur

class MonsieurTest(TestCase):
    def test_simple_point(self):
        dt = monsieur.this_minute()
        monsieur.incr('event', 1, [])

        self.assertEqual(len(DataPoint.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 0)
        self.assertEqual(len(DataAttribute.objects.all()), 0)

        dp = DataPoint.objects.all()[0]
        self.assertEqual(dp.name, 'event')
        self.assertEqual(dp.count, 1)
        self.assertEqual(dp.dt, dt)

    def test_single_tag_point(self):
        dt = monsieur.this_minute()
        monsieur.incr('event', 1, ['tag',])

        self.assertEqual(len(DataPoint.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 1)
        self.assertEqual(len(DataAttribute.objects.all()), 0)

        dp = DataPoint.objects.all()[0]
        self.assertEqual(dp.name, 'event')
        self.assertEqual(dp.count, 1)
        self.assertEqual(dp.dt, dt)

        tag = Tag.objects.all()[0]
        self.assertEqual(tag.name, 'tag')
        self.assertEqual(tag, dp.tags.all()[0])
        self.assertEqual(dp, tag.points.all()[0])
