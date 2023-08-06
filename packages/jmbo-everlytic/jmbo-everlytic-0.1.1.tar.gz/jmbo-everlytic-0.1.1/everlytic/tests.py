import time
from datetime import timedelta, date

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.db import connection, transaction

from foundry.models import Member
from everlytic.models import EverlyticProfile

from everlytic import api


class EverlyticTestCase(TestCase):

    def setUp(self):
        self.member_attrs = {
            'first_name': 'firstname',
            'last_name': 'lastname',
            'dob': timezone.now().date() - timedelta(days=22 * 365),
            'receive_email': True,
            'receive_sms': False
        }
        required_fields_str = ','.join(['first_name', 'last_name', \
            'email', 'dob', 'receive_sms', 'receive_email'])
        cursor = connection.cursor()
        cursor.execute("DELETE FROM preferences_registrationpreferences")
        cursor.execute("INSERT INTO preferences_preferences (id) VALUES (1)")
        cursor.execute("""INSERT INTO preferences_registrationpreferences (preferences_ptr_id, 
            raw_required_fields, raw_display_fields, raw_unique_fields, raw_field_order) VALUES (1, %s, '', '', '{}')""", \
            [required_fields_str])
        cursor.execute("INSERT INTO preferences_preferences_sites (preferences_id, site_id) VALUES (1, 1)")
        transaction.commit_unless_managed()

    def create_member(self):
        attrs = self.member_attrs.copy()
        # unique email and username for this test run
        id = "%f" % time.time()
        dot = id.rindex('.')
        id = id[dot - 7:dot] + id[dot+1:dot+4]
        attrs['username'] = 'user_%s' % id
        attrs['email'] = "%s@praekeltconsulting.com" % id
        member = Member(**attrs)
        member.set_password('password')
        member.save()
        return member

    def test_create_member(self):
        member = self.create_member()
        self.assertEqual(EverlyticProfile.objects.filter(member=member).count(), 1)
