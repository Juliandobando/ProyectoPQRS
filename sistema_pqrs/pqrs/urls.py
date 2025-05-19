# pqrs/urls.py

from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import PQRSViewSet

router = DefaultRouter()
router.register(r'api/pqrs', PQRSViewSet, basename='pqrs')

urlpatterns = [
    path('', views.index, name='index'),
    path('usuario/', views.pagina_usuario, name='pagina_usuario'),
    path('gestor/', views.pagina_gestor, name='pagina_gestor'),

    
    path('radicar/', views.radicar_pqrs, name='radicar_pqrs'),
    # Agrega más rutas conforme avances
     path('login/', views.login_cliente, name='login_cliente'),
     path('logout/', views.logout_cliente, name='logout_cliente'),
    path('dashboard/', views.dashboard_cliente, name='dashboard_cliente'),  # Ya lo dejamos listo
    path('consulta/', views.consultar_radicados, name='consultar_radicados'),
    path('detalle/<str:numero_radicado>/', views.detalle_pqrs, name='detalle_pqrs'),

    path('gestor/login/', views.login_gestor, name='login_gestor'),
    path('gestor/logout/', views.logout_gestor, name='logout_gestor'),
    path('gestor/panel/', views.panel_gestor, name='panel_gestor'),
    path('gestor/gestionar/<str:numero_radicado>/', views.gestionar_pqrs, name='gestionar_pqrs'),
    path('gestor/descargar/<str:numero_radicado>/', views.descargar_anexo, name='descargar_anexo'),
    path('gestor/reporte/pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),

    path('reenviar/<str:numero_radicado>/', views.reenviar_confirmacion, name='reenviar_confirmacion'),
    path('confirmacion/<str:numero_radicado>/', views.confirmacion_pqrs, name='confirmacion_pqrs'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),

    # urls.py
    path('superadmin/panel/', views.admin_panel, name='admin_panel'),
    path('superadmin/usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('superadmin/usuarios/crear/', views.crear_gestor, name='crear_gestor'),
    path('superadmin/usuarios/eliminar/<int:gestor_id>/', views.eliminar_gestor, name='eliminar_gestor'),
    path('superadmin/clientes/desactivar/<int:cliente_id>/', views.desactivar_cliente, name='desactivar_cliente'),

    path('superadmin/login/', views.login_admin, name='login_admin'),
    path('superadmin/logout/', views.logout_admin, name='logout_admin'),


]

urlpatterns += router.urls