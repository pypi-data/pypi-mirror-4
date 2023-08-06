# -*- coding: utf-8 -*-
from django.test import TestCase
from models import GroupStat, GroupStatistic
from vkontakte_groups.factories import GroupFactory

GROUP_ID = 30221121

class VkontakteGroupsStatisticTest(TestCase):

    def test_fetch_statistic(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        self.assertEqual(GroupStat.objects.count(), 0)

        group.fetch_statistic()
        self.assertNotEqual(GroupStat.objects.count(), 0)

        stat = GroupStat.objects.all()[0]
        self.assertTrue(stat.members > 0)
        self.assertTrue(stat.views > 0)
        self.assertTrue(stat.visitors > 0)
        self.assertTrue(stat.males > 0)
        self.assertTrue(stat.females > 0)
        self.assertNotEqual(stat.date, None)

    def test_fetch_statistic_via_api(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        self.assertEqual(GroupStatistic.objects.count(), 0)

        group.fetch_statistic(api=True)
        self.assertNotEqual(GroupStatistic.objects.count(), 0)

        stat = GroupStatistic.objects.all()[0]
        self.assertTrue(stat.views > 0)
        self.assertTrue(stat.visitors > 0)
        self.assertTrue(stat.males > 0)
        self.assertTrue(stat.females > 0)
        self.assertNotEqual(stat.date, None)