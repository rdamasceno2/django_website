
from django.contrib import admin
from django.urls import path, include

import api
from website.views import welcome
from users.views import user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome),
    path('api/v1/', include('api.urls')),
    path('users/<int:id>', user),

]