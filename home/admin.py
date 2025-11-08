from django.contrib import admin
from .models import Project, ImpactCounter, Milestone, Feedback, ContactMessage, Donation

# Register your models here.
admin.site.register(Project)
admin.site.register(ImpactCounter)
admin.site.register(Milestone)
admin.site.register(Feedback)
admin.site.register(ContactMessage)
admin.site.register(Donation)