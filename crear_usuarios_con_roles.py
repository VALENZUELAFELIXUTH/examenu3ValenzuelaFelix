import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_tienda.settings')
django.setup()

from django.contrib.auth.models import User, Group
from tienda.models import PerfilUsuario, Cliente  # 👈 importa tu modelo de perfil (ajusta si está en otra app)


# ====== CREAR GRUPOS (ROLES) ======
roles = ['vendedor', 'gerente', 'administrador']
for rol in roles:
    grupo, creado = Group.objects.get_or_create(name=rol)
    if creado:
        print(f"✅ Grupo creado: {rol}")
    else:
        print(f"ℹ️ Grupo existente: {rol}")

# ====== CREAR USUARIOS DE PRUEBA ======
usuarios = [
    ('vendedor1', 'vendedor123', 'vendedor'),
    ('gerente1', 'gerente123', 'gerente'),
]

for username, password, rol in usuarios:
    user, creado = User.objects.get_or_create(username=username)
    if creado:
        user.set_password(password)
        user.save()
        print(f"✅ Usuario '{username}' creado.")
    else:
        print(f"ℹ️ Usuario '{username}' ya existe.")

    # Asignar grupo
    grupo = Group.objects.get(name=rol)
    user.groups.set([grupo])

    # Crear perfil si no existe
    perfil, creado = PerfilUsuario.objects.get_or_create(user=user, rol=rol)
    if creado:
        print(f"🧩 Perfil creado para '{username}' con rol '{rol}'")
    else:
        print(f"ℹ️ Perfil de '{username}' ya existía")

# ====== CREAR CLIENTE CON USUARIO ======
cliente_username = 'cliente'
cliente_password = 'cliente123'

cliente_user, creado = User.objects.get_or_create(username=cliente_username)
if creado:
    cliente_user.set_password(cliente_password)
    cliente_user.save()
    print("✅ Usuario cliente creado")
else:
    print("ℹ️ Usuario cliente ya existe")

# Crear cliente en el modelo Cliente
cliente_obj, creado = Cliente.objects.get_or_create(
    usuario=cliente_user,
    defaults={
        'nombre': 'Charly',
        'apellido': 'Garcia',
        'email': 'Eldelostamales@gmail.com',
        'telefono': '6622019290',
        'direccion': 'Avenida Coronel Diaz y Santa Fe, barrio palermo #66',
    }
)

if creado:
    print("🧩 Cliente creado correctamente")
else:
    print("ℹ️ El cliente ya existía")
