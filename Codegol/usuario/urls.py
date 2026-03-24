from django.urls import path
from . import views 

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('usuario', views.usuario, name='usuario'),
    path('usuario/nuevo', views.crear_usuario, name="crear_usuario"),
    path('usuario/documento/<int:id>', views.documentos, name="documentos"),
    path('usuario/documento/eliminar/<int:id>/', views.borrar_documento, name='borrar_documento'),
    path('usuario/especifica/<int:id>', views.consulta_especifica_usuario, name="consulta_especifica_usuario"),
    path('usuario/editar/<int:id>', views.editar_usuario, name="editar_usuario"),
    path("usuario/mi-perfil/editar/", views.editar_mi_perfil, name="editar_mi_perfil"),
    path('eliminar/<int:id>', views.eliminar_usuario, name="eliminar_usuario"),
    path('reactivar/<int:id>', views.reactivar_usuario, name="reactivar_usuario"),
    path('usuario/inactivos/', views.usuarios_inactivos, name='usuarios_inactivos'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
