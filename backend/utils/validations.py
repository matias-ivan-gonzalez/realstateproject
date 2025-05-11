def tiene_permiso(usuario, permiso_nombre):
    return any(p.nombre == permiso_nombre for p in usuario.rol.permisos)
