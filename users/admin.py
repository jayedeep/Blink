from django.contrib import admin
from . models import User
# Register your models here.
# admin.site.register(User)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_of_birth','phone_number')


# Register the admin class with the associated model
admin.site.register(User, UserAdmin)