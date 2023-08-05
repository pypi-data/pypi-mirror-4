from django.contrib import admin

from .models import Company

class ContactableAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Address', {
            'fields': ('address_1', 'address_2', 'city', 'postcode',)
        }),
        ('Telephone', {
            'fields': ('landline', 'mobile', 'fax'),
        })
    )


class CompanyAdmin(ContactableAdmin):
    fieldsets = (
        ('Details', {
            'fields': ('name',)
        }),
    ) + ContactableAdmin.fieldsets

admin.site.register(Company, CompanyAdmin)
