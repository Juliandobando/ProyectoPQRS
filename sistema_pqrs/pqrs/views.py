# pqrs/views.py
# pqrs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail, BadHeaderError
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.db.models import Q
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from rest_framework import viewsets
from .models import PQRS
from .serializers import PQRSSerializer


from .forms import (
    LoginForm,
    PerfilClienteForm,
    RadicarPQRSForm,
    GestorLoginForm,
    GestionarPQRSForm,
    CrearUsuarioForm,
    AdminLoginForm
)

from .models import Cliente, PQRS, Gestor, Administrador, LogCambio
from .decoradores import solo_admin, login_requerido

import random
import string
import re
import os
from reportlab.pdfgen import canvas

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def pagina_usuario(request):
    return render(request, 'usuario.html')

def pagina_gestor(request):
    return render(request, 'pqrs/gestor.html')


# Create your views here.

class PQRSViewSet(viewsets.ModelViewSet):
    queryset = PQRS.objects.all().order_by('-fecha_radicado')
    serializer_class = PQRSSerializer

def login_admin(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                admin = Administrador.objects.get(username=username)
                if not admin.activo:
                    messages.error(request, "Tu cuenta de administrador está desactivada.")
                    return redirect('login_admin')
                
                elif check_password(password, admin.password):
                    request.session.flush()  # Limpia cualquier sesión anterior
                    request.session['admin_id'] = admin.id
                    request.session['rol'] = 'admin'
                    messages.success(request, "Bienvenido, administrador.")
                    return redirect('admin_panel')
                else:
                    messages.error(request, "Contraseña incorrecta.")
            except Administrador.DoesNotExist:
                messages.error(request, "Administrador no encontrado.")
    else:
        form = AdminLoginForm()

    return render(request, 'pqrs/login_admin.html', {'form': form})

def logout_admin(request):
    request.session.pop('admin_id', None)
    request.session.pop('rol', None)
    messages.info(request, "Sesión de administrador cerrada.")
    return redirect('login_admin')


#@solo_admin
#def admin_panel(request):
#    return render(request, 'pqrs/admin_panel.html')



def admin_panel(request):
    if request.session.get('rol') != 'admin':
        return redirect('login_admin')  # Este es el "name" de la ruta en urls.py
    return render(request, 'pqrs/admin_panel.html')



def listar_usuarios(request):
    if request.session.get('rol') != 'admin':
        return HttpResponse("Permiso denegado", status=403)

    clientes = Cliente.objects.all()
    gestores = Gestor.objects.all()
    return render(request, 'pqrs/listar_usuarios.html', {
        'clientes': clientes,
        'gestores': gestores
    })



def crear_gestor(request):
    if request.session.get('rol') != 'admin':
        return HttpResponse("Permiso denegado", status=403)

    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = make_password(form.cleaned_data['password'])

            if Gestor.objects.filter(username=username).exists():
                form.add_error('username', "Ya existe un gestor con este nombre.")
            else:
                Gestor.objects.create(username=username, password=password)
                messages.success(request, "Gestor creado exitosamente.")
                return redirect('listar_usuarios')
    else:
        form = CrearUsuarioForm()
    return render(request, 'pqrs/crear_gestor.html', {'form': form})

def eliminar_gestor(request, gestor_id):
    if request.session.get('rol') != 'admin':
        return HttpResponse("Permiso denegado", status=403)

    gestor = get_object_or_404(Gestor, id=gestor_id)
    gestor.delete()
    messages.success(request, "Gestor eliminado correctamente.")
    return redirect('listar_usuarios')

def desactivar_cliente(request, cliente_id):
    if request.session.get('rol') != 'admin':
        return HttpResponse("Permiso denegado", status=403)

    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.activo = False
    cliente.save()
    messages.success(request, "Cliente desactivado.")
    return redirect('listar_usuarios')




def index(request):
    return render(request, 'pqrs/index.html')


def generar_contraseña():
    while True:
        contraseña = get_random_string(6)
        if (any(c.islower() for c in contraseña) and
            any(c.isupper() for c in contraseña) and
            any(c.isdigit() for c in contraseña)):
            return contraseña

def generar_numero_radicado():
    fecha_str = now().strftime("%Y%m%d")
    while True:
        consecutivo = ''.join(random.choices(string.digits, k=4))
        numero = f'PQRS-{fecha_str}-{consecutivo}'
        if not PQRS.objects.filter(numero_radicado=numero).exists():
            return numero

def perfil_cliente(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('login_cliente')

    cliente = Cliente.objects.get(id=cliente_id)

    if request.method == 'POST':
        form = PerfilClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu información fue actualizada correctamente.")
            return redirect('dashboard_cliente')
    else:
        form = PerfilClienteForm(instance=cliente)

    return render(request, 'pqrs/perfil_cliente.html', {'form': form})


def radicar_pqrs(request):
    cliente_id = request.session.get('cliente_id')
    cliente = Cliente.objects.filter(id=cliente_id).first()

    # ----------------------
    # 1. Vista pública (sin sesión)
    # ----------------------
    if not cliente:
        if request.method == 'POST':
            form = RadicarPQRSForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                numero_id = data['numero_id']

                # Validar si ya existe un cliente con ese número_id
                if Cliente.objects.filter(numero_id=numero_id).exists():
                    form.add_error('numero_id', "Este número de identificación ya está registrado. Intenta iniciar sesión.")
                else:
                    # Crear cliente
                    contraseña_clara = generar_contraseña()
                    cliente = Cliente.objects.create(
                        tipo_id=data['tipo_id'],
                        numero_id=data['numero_id'],
                        nombre=data['nombre'],
                        correo=data['correo'],
                        telefono=data['telefono'],
                        contraseña=make_password(contraseña_clara)
                    )

                    # Crear PQRS
                    numero_radicado = generar_numero_radicado()
                    pqrs = PQRS.objects.create(
                        cliente=cliente,
                        tipo=data['tipo'],
                        comentarios=data['comentarios'],
                        archivo=data.get('archivo'),
                        numero_radicado=numero_radicado
                    )

                    # Enviar correo
                    try:
                        send_mail(
                            subject='Confirmación de PQRS',
                            message=f"Hola {cliente.nombre},\n\nTu PQRS ha sido radicada exitosamente.\n\nNúmero de radicado: {numero_radicado}\nContraseña: {contraseña_clara}",
                            from_email='no-reply@supermarket.com',
                            recipient_list=[cliente.correo],
                            fail_silently=False
                        )
                        pqrs.correo_enviado = True
                        pqrs.save()
                    except Exception as e:
                        messages.warning(request, "PQRS registrada, pero falló el envío del correo.")

                    return redirect('confirmacion_pqrs', numero_radicado=numero_radicado)
        else:
            form = RadicarPQRSForm()

        return render(request, 'pqrs/radicar_pqrs.html', {
            'form': form,
            'cliente_autenticado': False
        })

    # ----------------------
    # 2. Cliente autenticado
    # ----------------------
    else:
        if request.method == 'POST':
            form = RadicarPQRSForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data

                numero_radicado = generar_numero_radicado()
                pqrs = PQRS.objects.create(
                    cliente=cliente,
                    tipo=data['tipo'],
                    comentarios=data['comentarios'],
                    archivo=data.get('archivo'),
                    numero_radicado=numero_radicado
                )

                return redirect('confirmacion_pqrs', numero_radicado=numero_radicado)
        else:
            form = RadicarPQRSForm(initial={
                'tipo_id': cliente.tipo_id,
                'numero_id': cliente.numero_id,
                'nombre': cliente.nombre,
                'correo': cliente.correo,
                'telefono': cliente.telefono
            })

        return render(request, 'pqrs/radicar_pqrs.html', {
            'form': form,
            'cliente_autenticado': True
        })



def login_cliente(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            numero_id = form.cleaned_data['numero_id']
            contraseña = form.cleaned_data['contraseña']
            try:
                cliente = Cliente.objects.get(numero_id=numero_id)

                if not cliente.activo:
                    messages.error(request, 'Tu cuenta está desactivada.')
                    return redirect('login_cliente')
                
                if check_password(contraseña, cliente.contraseña):
                    request.session.flush()
                    request.session['cliente_id'] = cliente.id  # Guardamos sesión
                    request.session['rol'] = 'cliente'  # 🔐 Aquí guardamos el rol
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('dashboard_cliente')  # Redirige a su panel
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except Cliente.DoesNotExist:
                messages.error(request, 'Cliente no encontrado.')
    else:
        form = LoginForm()
    return render(request, 'pqrs/login.html', {'form': form})

def logout_cliente(request):
    request.session.flush()
    messages.info(request, "Sesión cerrada.")
    return redirect('login_cliente')


def dashboard_cliente(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('login_cliente')
    
    cliente = Cliente.objects.get(id=cliente_id)
    radicados = PQRS.objects.filter(cliente=cliente).order_by('-fecha_radicado')
    #return HttpResponse(f"Bienvenido {cliente.nombre}. Aquí verás tus PQRS.")
    return render(request, 'pqrs/dashboard.html', {'cliente': cliente, 'radicados': radicados})

def consultar_radicados(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('login_cliente')

    cliente = Cliente.objects.get(id=cliente_id)
    radicados = PQRS.objects.filter(cliente=cliente)

    # Filtro por número de radicado (opcional)
    filtro = request.GET.get('filtro')
    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')
    mensaje = ""

    if filtro:
        # Validar formato del número
        if not re.match(r'^PQRS-\d{8}-\d{4}$', filtro):
            mensaje = "Formato inválido. Usa: PQRS-YYYYMMDD-XXXX"
            #radicados = []
            radicados = PQRS.objects.none()
        else:
            radicados = radicados.filter(numero_radicado=filtro)
            if not radicados.exists():
                mensaje = "No se encontró ningún radicado"
    if tipo_filtro:
        radicados = radicados.filter(tipo=tipo_filtro)
    if estado_filtro:
        radicados = radicados.filter(estado=estado_filtro)   

    context = {
        'cliente': cliente,
        'radicados': radicados,
        'filtro': filtro,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'mensaje': mensaje
    }
    return render(request, 'pqrs/consulta_radicados.html', context)

def detalle_pqrs(request, numero_radicado):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('login_cliente')

    try:
        pqrs = PQRS.objects.get(numero_radicado=numero_radicado)
        if pqrs.cliente.id != cliente_id:
            return HttpResponse("Acceso no autorizado a este radicado", status=403)
    except PQRS.DoesNotExist:
        return HttpResponse("Radicado no encontrado", status=404)

    return render(request, 'pqrs/detalle_pqrs.html', {'pqrs': pqrs})

def login_gestor(request):
    if request.method == 'POST':
        form = GestorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                gestor = Gestor.objects.get(username=username)

                if not gestor.activo:
                    messages.error(request, 'Tu cuenta está desactivada.')
                    return redirect('login_gestor')
                
                if check_password(password, gestor.password):
                    request.session.flush()
                    request.session['gestor_id'] = gestor.id
                    request.session['rol'] = 'gestor'
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('panel_gestor')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except Gestor.DoesNotExist:
                messages.error(request, 'Gestor no encontrado.')
    else:
        form = GestorLoginForm()
    return render(request, 'pqrs/login_gestor.html', {'form': form})


def panel_gestor(request):
    gestor_id = request.session.get('gestor_id')
    if not gestor_id:
        return redirect('login_gestor')

    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')

    radicados = PQRS.objects.all().order_by('-fecha_radicado')

    if tipo_filtro:
        radicados = radicados.filter(tipo=tipo_filtro)
    if estado_filtro:
        radicados = radicados.filter(estado=estado_filtro)

    context = {
        'radicados': radicados,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'pqrs/panel_gestor.html', context)


def logout_gestor(request):
    request.session.pop('gestor_id', None)
    messages.info(request, "Sesión de gestor cerrada.")
    return redirect('login_gestor')

def gestionar_pqrs(request, numero_radicado):
    gestor_id = request.session.get('gestor_id')
    if not gestor_id:
        return redirect('login_gestor')

    try:
        pqrs = PQRS.objects.get(numero_radicado=numero_radicado)
    except PQRS.DoesNotExist:
        return HttpResponse("Radicado no encontrado", status=404)

    if request.method == 'POST':
        form = GestionarPQRSForm(request.POST, instance=pqrs)
        if form.is_valid():
            old_pqrs = PQRS.objects.get(pk=pqrs.pk) 
            form.save()
            campos = ['estado', 'justificacion']
            for campo in campos:
                valor_anterior = getattr(old_pqrs, campo)
                valor_nuevo = getattr(form.instance, campo)

                if valor_anterior != valor_nuevo:
                    LogCambio.objects.create(
                        pqrs=pqrs,
                        gestor=Gestor.objects.get(id=gestor_id),
                        campo_modificado=campo,
                        valor_anterior=valor_anterior,
                        valor_nuevo=valor_nuevo
                    )
            # Notificación al cliente (si el estado es "Resuelto")
            if pqrs.estado == 'RESUELTO':
                try:
                    send_mail(
                        subject='Tu PQRS ha sido resuelta',
                        message=f"Tu PQRS con número {pqrs.numero_radicado} ha sido resuelta.\n\nJustificación:\n{pqrs.justificacion}",
                        from_email='no-reply@supermarket.com',
                        recipient_list=[pqrs.cliente.correo],
                        fail_silently=True
                    )
                except Exception as e:
                    messages.warning(request, 'Cambio guardado, pero falló el envío del correo.')
            messages.success(request, 'PQRS actualizada correctamente.')
            return redirect('panel_gestor')
    else:
        form = GestionarPQRSForm(instance=pqrs)
    historial = LogCambio.objects.filter(pqrs=pqrs).order_by('-fecha')
    return render(request, 'pqrs/gestionar_pqrs.html', {'form': form, 'pqrs': pqrs, 'historial': historial})



def descargar_anexo(request, numero_radicado):
    gestor_id = request.session.get('gestor_id')
    if not gestor_id:
        return redirect('login_gestor')
    
    try:
        pqrs = PQRS.objects.get(numero_radicado=numero_radicado)
        if not pqrs.archivo:
            raise Http404("Archivo no disponible")

        archivo_path = pqrs.archivo.path

        if os.path.exists(archivo_path):
            return FileResponse(open(archivo_path, 'rb'), as_attachment=True)
        else:
            raise Http404("Archivo no disponible")
    except PQRS.DoesNotExist:
        raise Http404("PQRS no encontrada")

def generar_reporte_pdf(request):
    gestor_id = request.session.get('gestor_id')
    if not gestor_id:
        return redirect('login_gestor')

    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')

    radicados = PQRS.objects.all()
    if tipo_filtro:
        radicados = radicados.filter(tipo=tipo_filtro)
    if estado_filtro:
        radicados = radicados.filter(estado=estado_filtro)

    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_pqrs_{now().strftime("%Y%m%d_%H%M%S")}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - inch * 0.75, "Super Market")
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(width / 2, height - inch, "Reporte de PQRS")
        p.setFont("Helvetica", 10)

        y = height - inch * 1.5

        # Definir márgenes y espaciado
        left_margin = inch * 0.75
        line_height = 14

        # Column titles
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left_margin, y, "Número Radicado")
        p.drawString(left_margin + 120, y, "Tipo")
        p.drawString(left_margin + 200, y, "Estado")
        p.drawString(left_margin + 280, y, "Fecha")
        p.drawString(left_margin + 350, y, "Cliente")
        p.drawString(left_margin + 450, y, "Justificación")
        y -= line_height
        p.setFont("Helvetica", 10)

        for pqrs in radicados:
            if y < inch:
                p.showPage()
                y = height - inch
                # Repetir encabezado en nueva página
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - inch * 0.75, "Super Market")
                p.setFont("Helvetica-Bold", 12)
                p.drawCentredString(width / 2, height - inch, "Reporte de PQRS")
                p.setFont("Helvetica-Bold", 10)
                p.drawString(left_margin, y, "Número Radicado")
                p.drawString(left_margin + 120, y, "Tipo")
                p.drawString(left_margin + 200, y, "Estado")
                p.drawString(left_margin + 280, y, "Fecha")
                p.drawString(left_margin + 350, y, "Cliente")
                p.drawString(left_margin + 450, y, "Justificación")
                y -= line_height
                p.setFont("Helvetica", 10)

            # Justificación corta para evitar desbordes
            justificacion = pqrs.justificacion if pqrs.justificacion else ""
            if len(justificacion) > 50:
                justificacion = justificacion[:47] + "..."

            fecha_str = pqrs.fecha_radicado.strftime("%Y-%m-%d") if pqrs.fecha_radicado else "N/A"

            p.drawString(left_margin, y, pqrs.numero_radicado)
            p.drawString(left_margin + 120, y, pqrs.get_tipo_display())
            p.drawString(left_margin + 200, y, pqrs.get_estado_display())
            p.drawString(left_margin + 280, y, fecha_str)
            p.drawString(left_margin + 350, y, pqrs.cliente.nombre)
            p.drawString(left_margin + 450, y, justificacion)
            y -= line_height

        p.showPage()
        p.save()
        return response

    except Exception as e:
        messages.error(request, "Error generando reporte.")
        return redirect('panel_gestor')
    
def reenviar_confirmacion(request, numero_radicado):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('login_cliente')

    pqrs = get_object_or_404(PQRS, numero_radicado=numero_radicado, cliente_id=cliente_id)

    try:
        send_mail(
            subject='Reenvío de confirmación de PQRS',
            message=f"Hola {pqrs.cliente.nombre},\n\nEste es un reenvío de tu PQRS:\nNúmero de radicado: {pqrs.numero_radicado}",
            from_email='no-reply@supermarket.com',
            recipient_list=[pqrs.cliente.correo],
            fail_silently=False
        )
        messages.success(request, f"Correo reenviado correctamente para el radicado {pqrs.numero_radicado}.")
    except Exception as e:
        messages.error(request, "No se pudo reenviar el correo.")
    
    return redirect('dashboard_cliente')

def confirmacion_pqrs(request, numero_radicado):
    return render(request, 'pqrs/confirmacion_pqrs.html', {'numero_radicado': numero_radicado})

