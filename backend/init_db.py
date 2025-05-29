from database import db
from models.rol import Rol
from models.permiso import Permiso
from models.user import Cliente, Administrador, Encargado, SuperUsuario
from models.propiedad import Propiedad
from models.imagen import Imagen
from models.propiedad_administrador import propiedad_administrador
from models.favoritos import favoritos
from models.reserva import Reserva
from datetime import datetime, date


def init_db():
    # Roles
    rol_superusuario = Rol.query.filter_by(nombre='superusuario').first()
    if not rol_superusuario:
        rol_superusuario = Rol(nombre='superusuario')
        db.session.add(rol_superusuario)
    rol_admin = Rol.query.filter_by(nombre='admin').first()
    if not rol_admin:
        rol_admin = Rol(nombre='admin')
        db.session.add(rol_admin)
    rol_cliente = Rol.query.filter_by(nombre='cliente').first()
    if not rol_cliente:
        rol_cliente = Rol(nombre='cliente')
        db.session.add(rol_cliente)
    rol_encargado = Rol.query.filter_by(nombre='encargado').first()
    if not rol_encargado:
        rol_encargado = Rol(nombre='encargado')
        db.session.add(rol_encargado)
    db.session.commit()

    # Permisos
    
    crear_propiedad = Permiso.query.filter_by(nombre='crear_propiedad').first()
    if not crear_propiedad:
        crear_propiedad = Permiso(nombre='crear_propiedad')
        db.session.add(crear_propiedad)
    eliminar_propiedad = Permiso.query.filter_by(nombre='eliminar_propiedad').first()
    if not eliminar_propiedad:
        eliminar_propiedad = Permiso(nombre='eliminar_propiedad')
        db.session.add(eliminar_propiedad)
    modificar_propiedad = Permiso.query.filter_by(nombre='modificar_propiedad').first()
    if not modificar_propiedad:
        modificar_propiedad = Permiso(nombre='modificar_propiedad')
        db.session.add(modificar_propiedad)
    ver_propiedades = Permiso.query.filter_by(nombre='ver_propiedades').first()
    if not ver_propiedades:
        ver_propiedades = Permiso(nombre='ver_propiedades')
        db.session.add(ver_propiedades)
    
    crear_encargado = Permiso.query.filter_by(nombre='crear_encargado').first()
    if not crear_encargado:
        crear_encargado = Permiso(nombre='crear_encargado')
        db.session.add(crear_encargado)
    eliminar_encargado = Permiso.query.filter_by(nombre='eliminar_encargado').first()
    if not eliminar_encargado:
        eliminar_encargado = Permiso(nombre='eliminar_encargado')
        db.session.add(eliminar_encargado)
    
    asignar_propiedad_encargado = Permiso.query.filter_by(nombre='asignar_propiedad_encargado').first()
    if not asignar_propiedad_encargado:
        asignar_propiedad_encargado = Permiso(nombre='asignar_propiedad_encargado')
        db.session.add(asignar_propiedad_encargado)
    desasignar_propiedad_encargado = Permiso.query.filter_by(nombre='desasignar_propiedad_encargado').first()
    if not desasignar_propiedad_encargado:
        desasignar_propiedad_encargado = Permiso(nombre='desasignar_propiedad_encargado')
        db.session.add(desasignar_propiedad_encargado)
    
    crear_admin = Permiso.query.filter_by(nombre='crear_admin').first()
    if not crear_admin:
        crear_admin = Permiso(nombre='crear_admin')
        db.session.add(crear_admin)
    eliminar_admin = Permiso.query.filter_by(nombre='eliminar_admin').first()
    if not eliminar_admin:
        eliminar_admin = Permiso(nombre='eliminar_admin')
        db.session.add(eliminar_admin)
    
    ver_encargados = Permiso.query.filter_by(nombre='ver_encargados').first()
    if not ver_encargados:
        ver_encargados = Permiso(nombre='ver_encargados')
        db.session.add(ver_encargados)
    ver_administradores = Permiso.query.filter_by(nombre='ver_administradores').first()
    if not ver_administradores:
        ver_administradores = Permiso(nombre='ver_administradores')
        db.session.add(ver_administradores)
    añadir_favorito = Permiso.query.filter_by(nombre='añadir_favorito').first()
    if not añadir_favorito:
        añadir_favorito = Permiso(nombre='añadir_favorito')
        db.session.add(añadir_favorito)
    eliminar_favorito = Permiso.query.filter_by(nombre='eliminar_favorito').first()
    if not eliminar_favorito:
        eliminar_favorito = Permiso(nombre='eliminar_favorito')
        db.session.add(eliminar_favorito)
        
    # Asignar permisos a roles de forma segura
    if crear_propiedad not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(crear_propiedad)
    if eliminar_propiedad not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(eliminar_propiedad)
    if modificar_propiedad not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(modificar_propiedad)
    if ver_propiedades not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(ver_propiedades)
    if crear_encargado not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(crear_encargado)
    if eliminar_encargado not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(eliminar_encargado)
    if asignar_propiedad_encargado not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(asignar_propiedad_encargado)
    if desasignar_propiedad_encargado not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(desasignar_propiedad_encargado)
    if crear_admin not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(crear_admin)
    if eliminar_admin not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(eliminar_admin)
    if ver_encargados not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(ver_encargados)
    if ver_administradores not in rol_superusuario.permisos:
        rol_superusuario.permisos.append(ver_administradores)
    
    if crear_propiedad not in rol_admin.permisos:
        rol_admin.permisos.append(crear_propiedad)
    if eliminar_propiedad not in rol_admin.permisos:
        rol_admin.permisos.append(eliminar_propiedad)
    if modificar_propiedad not in rol_admin.permisos:
        rol_admin.permisos.append(modificar_propiedad)
    if ver_propiedades not in rol_admin.permisos:
        rol_admin.permisos.append(ver_propiedades)
    if crear_encargado not in rol_admin.permisos:
        rol_admin.permisos.append(crear_encargado)
    if eliminar_encargado not in rol_admin.permisos:
        rol_admin.permisos.append(eliminar_encargado)
    if asignar_propiedad_encargado not in rol_admin.permisos:
        rol_admin.permisos.append(asignar_propiedad_encargado)
    if desasignar_propiedad_encargado not in rol_admin.permisos:
        rol_admin.permisos.append(desasignar_propiedad_encargado)
    if ver_encargados not in rol_admin.permisos:
        rol_admin.permisos.append(ver_encargados)
    if ver_administradores not in rol_admin.permisos:
        rol_admin.permisos.append(ver_administradores)
    
    if ver_propiedades not in rol_encargado.permisos:
        rol_encargado.permisos.append(ver_propiedades)
    
    if añadir_favorito not in rol_cliente.permisos:
        rol_cliente.permisos.append(añadir_favorito)
    if eliminar_favorito not in rol_cliente.permisos:
        rol_cliente.permisos.append(eliminar_favorito)
    
    db.session.commit()

    # Usuarios
    superuser = SuperUsuario.query.filter_by(email='sofia.garcia@admin.com').first()
    if not superuser:
        superuser = SuperUsuario(nombre='Sofía', apellido='García', dni='30123456', email='sofia.garcia@admin.com', contrasena='adminSG1', telefono='1134567890', nacionalidad='Argentina', rol=rol_superusuario)
        db.session.add(superuser)
    admin = Administrador.query.filter_by(email='martin.perez@admin.com').first()
    if not admin:
        admin = Administrador(nombre='Martín', apellido='Pérez', dni='32123456', email='martin.perez@admin.com', contrasena='adminMP2', telefono='1145678901', nacionalidad='Argentina', rol=rol_admin)
        db.session.add(admin)
    encargado = Encargado.query.filter_by(email='lucia.fernandez@encargado.com').first()
    if not encargado:
        encargado = Encargado(nombre='Lucía', apellido='Fernández', dni='34123456', email='lucia.fernandez@encargado.com', contrasena='encargLF3', telefono='1156789012', nacionalidad='Argentina', rol=rol_encargado)
        db.session.add(encargado)

    cliente = Cliente.query.filter_by(email='juan.lopez@cliente.com').first()
    if not cliente:
        cliente = Cliente(
            nombre='Juan', apellido='López', dni='36123456', email='juan.lopez@cliente.com',
            contrasena='clienteJL4', telefono='1167890123', nacionalidad='Argentina', rol=rol_cliente,
            direccion='Av. Corrientes 1234, CABA', fecha_nacimiento=date(1990, 5, 15)
        )
        db.session.add(cliente)
    encargado2 = Encargado.query.filter_by(email='marcos.silva@encargado.com').first()
    if not encargado2:
        encargado2 = Encargado(nombre='Marcos', apellido='Silva', dni='35123456', email='marcos.silva@encargado.com', contrasena='encargMS4', telefono='1178901234', nacionalidad='Argentina', rol=rol_encargado)
        db.session.add(encargado2)
    db.session.commit()

    # Propiedades
    prop1 = Propiedad.query.filter_by(nombre='Casa Palermo').first()
    if not prop1:
        prop1 = Propiedad(nombre='Casa Palermo', ubicacion='Palermo, CABA', direccion='Gorriti 4800, Palermo, CABA', precio=250000, cantidad_habitaciones=4, limite_personas=7, pet_friendly=True, cochera=True, wifi=True, piscina=True, patio_trasero=True, descripcion='Casa moderna con pileta y jardín en el corazón de Palermo.', superusuario=superuser, encargado=encargado, latitud=-34.5831, longitud=-58.4246)
        db.session.add(prop1)
    else:
        prop1.latitud = -34.5831
        prop1.longitud = -58.4246
    prop2 = Propiedad.query.filter_by(nombre='Depto Recoleta').first()
    if not prop2:
        prop2 = Propiedad(nombre='Depto Recoleta', ubicacion='Recoleta, CABA', direccion='Arenales 2100, Recoleta, CABA', precio=180000, cantidad_habitaciones=3, limite_personas=5, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=False, descripcion='Departamento elegante cerca de Plaza Francia.', superusuario=superuser, encargado=encargado, latitud=-34.5895, longitud=-58.3936)
        db.session.add(prop2)
    else:
        prop2.latitud = -34.5895
        prop2.longitud = -58.3936
    prop3 = Propiedad.query.filter_by(nombre='Casa San Isidro').first()
    if not prop3:
        prop3 = Propiedad(nombre='Casa San Isidro', ubicacion='San Isidro, Buenos Aires', direccion='Av. del Libertador 16200, San Isidro, Buenos Aires', precio=320000, cantidad_habitaciones=5, limite_personas=8, pet_friendly=True, cochera=True, wifi=True, piscina=True, patio_trasero=True, descripcion='Amplia casa familiar con parque y pileta en zona norte.', superusuario=superuser, encargado=encargado, latitud=-34.4732, longitud=-58.5122)
        db.session.add(prop3)
    else:
        prop3.latitud = -34.4732
        prop3.longitud = -58.5122
    prop4 = Propiedad.query.filter_by(nombre='Depto Rosario Centro').first()
    if not prop4:
        prop4 = Propiedad(nombre='Depto Rosario Centro', ubicacion='Rosario, Santa Fe', direccion='Córdoba 1200, Rosario, Santa Fe', precio=95000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=False, descripcion='Departamento céntrico a metros del Monumento a la Bandera.', superusuario=superuser, encargado=encargado, latitud=-32.9468, longitud=-60.6393)
        db.session.add(prop4)
    else:
        prop4.latitud = -32.9468
        prop4.longitud = -60.6393
    prop5 = Propiedad.query.filter_by(nombre='Casa Bariloche Lago').first()
    if not prop5:
        prop5 = Propiedad(nombre='Casa Bariloche Lago', ubicacion='San Carlos de Bariloche, Río Negro', direccion='Av. Bustillo Km 8, San Carlos de Bariloche, Río Negro', precio=400000, cantidad_habitaciones=6, limite_personas=10, pet_friendly=True, cochera=True, wifi=True, piscina=True, patio_trasero=True, descripcion='Casa de lujo con vista al lago Nahuel Huapi.', superusuario=superuser, encargado=encargado, latitud=-41.0999, longitud=-71.4196)
        db.session.add(prop5)
    else:
        prop5.latitud = -41.0999
        prop5.longitud = -71.4196
    prop6 = Propiedad.query.filter_by(nombre='Depto Mendoza Centro').first()
    if not prop6:
        prop6 = Propiedad(nombre='Depto Mendoza Centro', ubicacion='Mendoza', direccion='Av. San Martín 800, Mendoza', precio=110000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=False, descripcion='Departamento moderno en pleno centro de Mendoza.', superusuario=superuser, encargado=encargado, latitud=-32.8908, longitud=-68.8447)
        db.session.add(prop6)
    else:
        prop6.latitud = -32.8908
        prop6.longitud = -68.8447
    prop7 = Propiedad.query.filter_by(nombre='Casa Córdoba Nueva Córdoba').first()
    if not prop7:
        prop7 = Propiedad(nombre='Casa Córdoba Nueva Córdoba', ubicacion='Córdoba', direccion='Obispo Trejo 1200, Nueva Córdoba, Córdoba', precio=210000, cantidad_habitaciones=3, limite_personas=6, pet_friendly=True, cochera=True, wifi=True, piscina=False, patio_trasero=True, descripcion='Casa amplia cerca del Parque Sarmiento.', superusuario=superuser, encargado=encargado, latitud=-31.4273, longitud=-64.1830)
        db.session.add(prop7)
    else:
        prop7.latitud = -31.4273
        prop7.longitud = -64.1830
    prop8 = Propiedad.query.filter_by(nombre='Depto Mar del Plata Playa').first()
    if not prop8:
        prop8 = Propiedad(nombre='Depto Mar del Plata Playa', ubicacion='Mar del Plata, Buenos Aires', direccion='Boulevard Marítimo 2200, Mar del Plata, Buenos Aires', precio=130000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=False, descripcion='Departamento con vista al mar, a metros de Playa Bristol.', superusuario=superuser, encargado=encargado, latitud=-38.0055, longitud=-57.5426)
        db.session.add(prop8)
    else:
        prop8.latitud = -38.0055
        prop8.longitud = -57.5426
    prop9 = Propiedad.query.filter_by(nombre='Casa Tigre Delta').first()
    if not prop9:
        prop9 = Propiedad(nombre='Casa Tigre Delta', ubicacion='Tigre, Buenos Aires', direccion='Río Sarmiento 300, Tigre, Buenos Aires', precio=270000, cantidad_habitaciones=4, limite_personas=8, pet_friendly=True, cochera=True, wifi=True, piscina=True, patio_trasero=True, descripcion='Casa isleña con muelle propio en el Delta de Tigre.', superusuario=superuser, encargado=encargado, latitud=-34.4089, longitud=-58.5796)
        db.session.add(prop9)
    else:
        prop9.latitud = -34.4089
        prop9.longitud = -58.5796
    prop10 = Propiedad.query.filter_by(nombre='Depto Salta Balcarce').first()
    if not prop10:
        prop10 = Propiedad(nombre='Depto Salta Balcarce', ubicacion='Salta', direccion='Balcarce 500, Salta', precio=90000, cantidad_habitaciones=2, limite_personas=3, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=False, descripcion='Departamento turístico en la zona de peñas y bares.', superusuario=superuser, encargado=encargado, latitud=-24.7883, longitud=-65.4106)
        db.session.add(prop10)
    else:
        prop10.latitud = -24.7883
        prop10.longitud = -65.4106
    db.session.commit()

    # Relación muchos-a-muchos administradores-propiedades
    if admin not in prop1.administradores:
        prop1.administradores.append(admin)
    if admin not in prop2.administradores:
        prop2.administradores.append(admin)
    if admin not in prop3.administradores:
        prop3.administradores.append(admin)
    if admin not in prop4.administradores:
        prop4.administradores.append(admin)
    if admin not in prop5.administradores:
        prop5.administradores.append(admin)
    if admin not in prop6.administradores:
        prop6.administradores.append(admin)
    if admin not in prop7.administradores:
        prop7.administradores.append(admin)
    if admin not in prop8.administradores:
        prop8.administradores.append(admin)
    if admin not in prop9.administradores:
        prop9.administradores.append(admin)
    if admin not in prop10.administradores:
        prop10.administradores.append(admin)
    
        
    # Reservas
    fecha_inicio = '2025-6-24'	
    fecha_fin = '2025-6-30'
    fecha_inicio_convertida = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin_convertida = datetime.strptime(fecha_fin, '%Y-%m-%d')
    reserva1 = Reserva.query.filter_by(cliente_id=cliente.id, propiedad_id=prop1.id, fecha_inicio=fecha_inicio_convertida, fecha_fin=fecha_fin_convertida).first()
    if not reserva1:
        reserva1 = Reserva(cliente=cliente, propiedad=prop1, fecha_inicio=fecha_inicio_convertida, fecha_fin=fecha_fin_convertida, cantidad_personas=3)
        db.session.add(reserva1)
        
    
    db.session.commit()

    # Favoritos
    if prop1 not in cliente.favoritos:
        cliente.favoritos.append(prop1)
    db.session.commit()

    # Imagenes
   
    img1 = Imagen(url='img/prop1/img1.jpeg', nombre_archivo='Primera foto', propiedad=prop1)
    db.session.add(img1)
    prop1.imagenes.append(img1)
    
    img2 = Imagen(url='img/prop2/Diseno-casa-familiar-el-bambu-3.jpg', nombre_archivo='img2.jpg', propiedad=prop2)
    db.session.add(img2)
    prop2.imagenes.append(img2)
    
    img3 = Imagen(url='img/prop3/download.jpeg', nombre_archivo='img3.jpg', propiedad=prop3)
    db.session.add(img3)
    prop3.imagenes.append(img3)
    
    
    db.session.commit() 