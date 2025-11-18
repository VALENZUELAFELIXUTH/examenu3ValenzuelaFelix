import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_tienda.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Definir los roles
roles = ['Vendedor', 'Gerente', 'Administrador']

for rol in roles:
    group, created = Group.objects.get_or_create(name=rol)
    if created:
        print(f'✅ Rol creado: {rol}')
    else:
        print(f'ℹ️ Rol ya existía: {rol}')

# Crear usuarios y asignarles roles
usuarios = [
    ('vendedor1', 'vendedor123', 'Vendedor'),
    ('gerente1', 'gerente123', 'Gerente'),
    ('admin1', 'admin123', 'Administrador'),
]

for username, password, rol in usuarios:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
        user.groups.add(Group.objects.get(name=rol))
        print(f'✅ Usuario creado: {username} ({rol})')
    else:
        print(f'ℹ️ Usuario ya existía: {username}')

print("\n✨ Creación de usuarios y roles completada.")