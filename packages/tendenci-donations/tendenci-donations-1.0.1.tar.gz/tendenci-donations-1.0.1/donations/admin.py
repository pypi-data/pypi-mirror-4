from django.contrib import admin
from donations.models import Donation
from donations.forms import DonationAdminForm

class DonationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'donation_amount', 'payment_method']
    form = DonationAdminForm

admin.site.register(Donation, DonationAdmin)
