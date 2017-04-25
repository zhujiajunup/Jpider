import sys
import os
import django

sys.path.append('../../../Jpider')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()