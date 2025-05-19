EXCLUDED_MODULES = [
    'models/__initi__.py',
    'models/__init__.py',
    '__init__.py',
]

# ...lógica previa...
# Cuando verifiques los archivos que faltan, ignora los que estén en EXCLUDED_MODULES
faltan = [f for f in faltan if f not in EXCLUDED_MODULES]
# ... resto del código ... 