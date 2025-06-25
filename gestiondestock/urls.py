from django.contrib import admin
from django.urls import path, include


urlpatterns = [
  #  path('jet/', include('jet_reboot.urls', 'jet_reboot')),     
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('carbone/', include('carbone.urls')), 
]
