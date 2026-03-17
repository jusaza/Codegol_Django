from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('usuario', views.usuario, name='usuario'),
    path('usuario/nuevo', views.crear_usuario, name="crear_usuario"),
    path('usuario/especifica/<int:id>', views.consulta_especifica_usuario, name="consulta_especifica_usuario"),
    path('usuario/editar/<int:id>', views.editar_usuario, name="editar_usuario"),
    path('eliminar/<int:id>', views.eliminar_usuario, name="eliminar"),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
