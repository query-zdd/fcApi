from django.test import TestCase
import datetime
# Create your tests here.
# a=datetime.datetime(2018, 1, 1, 12, 50, 12, 10)
dt = datetime.datetime.now()- datetime.timedelta(seconds=3600)
print(dt)
print(datetime.datetime.now())