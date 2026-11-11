from django.contrib import admin

from .models import Project, Stage, Task, Team

# Note e TimeEntry ficam de fora: são registros privados de quem os cadastrou.
admin.site.register([Team, Project, Stage, Task])
