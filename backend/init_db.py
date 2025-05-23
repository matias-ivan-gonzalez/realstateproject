from database import db
from models.rol import Rol
from models.permiso import Permiso
from models.user import Cliente, Administrador, Encargado, SuperUsuario
from models.propiedad import Propiedad
from models.imagen import Imagen
from models.propiedad_administrador import propiedad_administrador
from models.favoritos import favoritos
from models.reserva import Reserva
from datetime import datetime


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
    superuser = SuperUsuario.query.filter_by(email='super@user.com').first()
    if not superuser:
        superuser = SuperUsuario(nombre='Super', apellido='User', dni='100', email='super@user.com', contrasena='123', telefono='123', nacionalidad='AR', rol=rol_superusuario)
        db.session.add(superuser)
    admin = Administrador.query.filter_by(email='admin@uno.com').first()
    if not admin:
        admin = Administrador(nombre='Admin', apellido='Uno', dni='101', email='admin@uno.com', contrasena='123', telefono='123', nacionalidad='AR', rol=rol_admin)
        db.session.add(admin)
    encargado = Encargado.query.filter_by(email='encargado@uno.com').first()
    if not encargado:
        encargado = Encargado(nombre='Encargado', apellido='Uno', dni='102', email='encargado@uno.com', contrasena='123', telefono='123', nacionalidad='AR', rol=rol_encargado)
        db.session.add(encargado)
    cliente = Cliente.query.filter_by(email='cliente@uno.com').first()
    if not cliente:
        cliente = Cliente(nombre='Cliente', apellido='Uno', dni='103', email='cliente@uno.com', contrasena='123', telefono='123', nacionalidad='AR', rol=rol_cliente)
        db.session.add(cliente)
    db.session.commit()

    # Propiedades
    prop1 = Propiedad.query.filter_by(nombre='Casa Centro').first()
    if not prop1:
        prop1 = Propiedad(nombre='Casa Centro', ubicacion='Calle Falsa 123', precio=100000, cantidad_habitaciones=3, limite_personas=5, pet_friendly=True, cochera=True, wifi=True, piscina=False, patio_trasero=True, descripcion='Linda casa', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop1)
    else:
        prop1.latitud = -34.6037
        prop1.longitud = -58.3816
    prop2 = Propiedad.query.filter_by(nombre='Depto Norte').first()
    if not prop2:
        prop2 = Propiedad(nombre='Depto Norte', ubicacion='Avenida Siempreviva 742', precio=80000, cantidad_habitaciones=2, limite_personas=3, pet_friendly=False, cochera=False, wifi=True, piscina=True, patio_trasero=False, descripcion='Departamento moderno', superusuario=superuser, encargado=encargado, latitud=-34.5955, longitud=-58.3932)
        db.session.add(prop2)
    else:
        prop2.latitud = -34.5955
        prop2.longitud = -58.3932
    prop3 = Propiedad.query.filter_by(nombre='Casa Sur').first()
    if not prop3:
        prop3 = Propiedad(nombre='Casa Sur', ubicacion='Calle Falsa 456', precio=120000, cantidad_habitaciones=4, limite_personas=6, pet_friendly=True, cochera=True, wifi=False, piscina=True, patio_trasero=True, descripcion='Casa amplia', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop3)
    prop4 = Propiedad.query.filter_by(nombre='Depto Sur').first()
    if not prop4:
        prop4 = Propiedad(nombre='Depto Sur', ubicacion='Avenida Siempreviva 123', precio=90000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=True, descripcion='Departamento acogedor', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop4)
    prop5 = Propiedad.query.filter_by(nombre='Casa Este').first()
    if not prop5:
        prop5 = Propiedad(nombre='Casa Este', ubicacion='Calle Falsa 789', precio=110000, cantidad_habitaciones=3, limite_personas=5, pet_friendly=True, cochera=True, wifi=True, piscina=False, patio_trasero=False, descripcion='Casa con jardín', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop5)
    prop6 = Propiedad.query.filter_by(nombre='Depto Oeste').first()
    if not prop6:
        prop6 = Propiedad(nombre='Depto Oeste', ubicacion='Avenida Siempreviva 456', precio=95000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=True, patio_trasero=False, descripcion='Departamento luminoso', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop6)
    prop7 = Propiedad.query.filter_by(nombre='Casa Oeste').first()
    if not prop7:
        prop7 = Propiedad(nombre='Casa Oeste', ubicacion='Calle Falsa 321', precio=130000, cantidad_habitaciones=5, limite_personas=7, pet_friendly=True, cochera=True, wifi=False, piscina=True, patio_trasero=True, descripcion='Casa con pileta', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop7)
    prop8 = Propiedad.query.filter_by(nombre='Depto Este').first()
    if not prop8:
        prop8 = Propiedad(nombre='Depto Este', ubicacion='Avenida Siempreviva 789', precio=85000, cantidad_habitaciones=2, limite_personas=3, pet_friendly=False, cochera=False, wifi=True, piscina=False, patio_trasero=True, descripcion='Departamento pequeño', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop8)
    prop9 = Propiedad.query.filter_by(nombre='Casa Norte').first()
    if not prop9:
        prop9 = Propiedad(nombre='Casa Norte', ubicacion='Calle Falsa 654', precio=140000, cantidad_habitaciones=6, limite_personas=8, pet_friendly=True, cochera=True, wifi=True, piscina=False, patio_trasero=False, descripcion='Casa moderna', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop9)
    prop10 = Propiedad.query.filter_by(nombre='Depto Centro').first()
    if not prop10:
        prop10 = Propiedad(nombre='Depto Centro', ubicacion='Avenida Siempreviva 321', precio=105000, cantidad_habitaciones=2, limite_personas=4, pet_friendly=False, cochera=False, wifi=True, piscina=True, patio_trasero=False, descripcion='Departamento céntrico', superusuario=superuser, encargado=encargado, latitud=-34.6037, longitud=-58.3816)
        db.session.add(prop10)
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
    from sqlalchemy import and_
    img1 = Imagen.query.filter(and_(Imagen.nombre_archivo=='img1.jpg', Imagen.propiedad_id==prop1.id)).first()
    if not img1:
        img1 = Imagen(url='http://img1.com', nombre_archivo='img1.jpg', propiedad=prop1)
        db.session.add(img1)
    img2 = Imagen.query.filter(and_(Imagen.nombre_archivo=='img2.jpg', Imagen.propiedad_id==prop2.id)).first()
    if not img2:
        img2 = Imagen(url='http://img2.com', nombre_archivo='img2.jpg', propiedad=prop2)
        db.session.add(img2)
    db.session.commit() 