from django.contrib import admin
from autograde.models import *
admin.site.register(TestCase)
admin.site.register(ProjectFile)
admin.site.register(Project)
admin.site.register(TestResult)
