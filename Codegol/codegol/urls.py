"""
URL configuration for codegol project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),
    # paginas generales
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('pagina_original/', views.pagina_original, name='pagina_original'),
    path('400/', views.error400, name='error400'),

    path('entrenamientos/', include('entrenamientos.urls')),
    path('inventario/', include('inventario.urls')),
    path('matricula/', include('matricula.urls')),
]

