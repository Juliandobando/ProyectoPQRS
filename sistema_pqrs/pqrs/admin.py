from django.contrib import admin
from .models import Cliente, PQRS, Gestor

# Register your models here.
admin.site.register(Cliente)
admin.site.register(PQRS)
admin.site.register(Gestor)
#admin.site.register(Usuario)