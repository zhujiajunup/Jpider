import sys
import os
import django
import django.db.models
sys.path.append('../Jpider')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()

from spiders.models import BaiKeRank

ranks = BaiKeRank.objects.all().order_by('rank')
for r in ranks:
    print(r)

