
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404
from write.views import custom_404

handler404 = custom_404

urlpatterns = [
    path('interview/write/', include('write.urls')),
    path('interview/admin/management/', include('management.urls')),
    path('interview/admin/', admin.site.urls),
]
