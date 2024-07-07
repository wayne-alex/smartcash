from django.contrib import admin
from .models import Account, Withdraw, Deposit,Package,Profile,Affiliate

admin.site.register(Account)
admin.site.register(Profile)
admin.site.register(Deposit)
admin.site.register(Package)
admin.site.register(Withdraw)
admin.site.register(Affiliate)

# Register your models here.
