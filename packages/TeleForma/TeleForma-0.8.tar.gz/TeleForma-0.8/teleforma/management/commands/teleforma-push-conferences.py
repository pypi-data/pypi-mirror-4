from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from telemeta.models import *
from telemeta.util.unaccent import unaccent
from teleforma.models import *
from teleforma.views import *
from django.contrib.auth.models import User

import logging
import json

class Command(BaseCommand):
    help = "Export professors to a JSON file"
    args = "path"
    admin_email = 'webmaster@parisson.com'


    def handle(self, *args, **options):
        c = Conference()
        c.public_id='2907fca29def0999633b5132c9b96727'
        c.course = Course.objects.get(code='OB')
        c.course_type = CourseType.objects.get(name='Cours')
        c.professor = Professor.objects.get(user=User.objects.get(username='a.cormier'))
        c.session = '1'
        c.room = Room.objects.get(name='Augustins')
        dict = c.to_json_dict()
        v = ConferenceRecordView()
        v.push(c)




