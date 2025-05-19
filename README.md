# ProyectoPQRS


🛠 INSTRUCCIONES PARA INSTALAR Y EJECUTAR EL SISTEMA PQRS - SUPERMARKET (DJANGO)

------------------------------------------------------------
✅ 1. VERIFICA TU VERSIÓN DE PYTHON
------------------------------------------------------------
python --version

✅ Debes tener Python 3.10 o superior instalado.

------------------------------------------------------------
✅ 2. CREAR ENTORNO VIRTUAL
------------------------------------------------------------
python -m venv venv

Activar entorno en Windows:
venv\Scripts\activate

✅ Se debe ver así en la terminal:
(venv) C:\Users\TuNombre\sistema_pqrs>

------------------------------------------------------------
✅ 3. INSTALAR DEPENDENCIAS
------------------------------------------------------------
pip install --upgrade pip
pip install -r requirements.txt

(Si no tienes requirements.txt, puedes usar estos comandos:)
pip install django
pip install django-widget-tweaks
pip install djangorestframework
pip install bcrypt
pip install reportlab

------------------------------------------------------------
✅ 4. CREAR PROYECTO Y APP (SI INICIAS DE CERO)
------------------------------------------------------------
django-admin startproject supermarket_pqrs .
python manage.py startapp pqrs

------------------------------------------------------------
✅ 5. MIGRACIONES DE BASE DE DATOS
------------------------------------------------------------
python manage.py makemigrations
python manage.py migrate

------------------------------------------------------------
✅ 6. CREAR SUPERUSUARIO PARA ADMINISTRADOR
------------------------------------------------------------
python manage.py createsuperuser

Recomendación:
Usuario: admin1
Contraseña: 3105861612romeo

------------------------------------------------------------
✅ 7. EJECUTAR EL SERVIDOR
------------------------------------------------------------
python manage.py runserver

👉 Abrir navegador en http://127.0.0.1:8000/

------------------------------------------------------------
✅ 8. CREAR CLIENTE DE PRUEBA (CONSOLA INTERACTIVA)
------------------------------------------------------------
python manage.py shell

>>> from pqrs.models import Cliente
>>> from django.contrib.auth.hashers import make_password

>>> Cliente.objects.create(
    tipo_id="CC",
    numero_id="123456789",
    nombre="Cliente de Prueba",
    correo="cliente@correo.com",
    telefono="1234567890",
    contraseña=make_password("Test123")
)

Debe mostrar:
<Cliente: Cliente de Prueba (123456789)>

------------------------------------------------------------
✅ 9. USUARIOS DE PRUEBA PARA INGRESAR
------------------------------------------------------------
| Rol           | Usuario      | Contraseña        |
|---------------|--------------|-------------------|
| Administrador | admin1       | MiClaveSegura123  |
| Gestor 1      | gestor2      | gestor2           |
| Gestor 2      | gestorpqrs   | 12345             |
| Cliente       | vivas        | G5Xukn            |
| Cliente prueba| 123456789    | Test123           |

------------------------------------------------------------
✅ 10. SI CERRASTE LA TERMINAL Y VAS A REABRIR
------------------------------------------------------------
cd sistema_pqrs
venv\Scripts\activate
python manage.py runserver

------------------------------------------------------------
📝 NOTAS ADICIONALES
------------------------------------------------------------
- Verificar si un paquete está instalado:
  pip show reportlab

- Limpiar base de datos (opcional):
  python manage.py flush
