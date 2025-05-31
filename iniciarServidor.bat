@echo off
REM Restaurar imágenes desde backup antes de iniciar el servidor
call restore_images_from_backup.bat

REM Borrar la base de datos
call borrarDB.bat

REM Iniciar el servidor en primer plano (sincrónico)
python backend\run.py

REM Esperar 5 segundos para asegurarse de que el servidor se cerró (opcional)
timeout /t 5

REM Hacer curl a todas las rutas que hay en el archivo routes
for /f "tokens=2 delims=\"\"" %%a in ('findstr /R "@app\.route" backend\routes.py') do (
    echo Haciendo curl a: %%a
    curl http://127.0.0.1:5000%%a
)

pause