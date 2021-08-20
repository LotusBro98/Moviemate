from django.contrib import admin
from .models import Movie, Episode, User, Party, Invitation

# Register your models here.
admin.site.register(Movie)
admin.site.register(Episode)
admin.site.register(User)
admin.site.register(Party)
admin.site.register(Invitation)