from django.contrib import admin

from .models import Note, Project, Stage, Task, Team

admin.site.register([Team, Project, Stage, Task, Note])
