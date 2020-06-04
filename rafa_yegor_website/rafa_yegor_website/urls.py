
from django.contrib import admin
from django.urls import path, include

import api
from website.views import welcome


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome),
    path('api/v1/', include('api.urls')),
]