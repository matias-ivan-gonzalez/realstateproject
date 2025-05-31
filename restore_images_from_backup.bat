@echo off
REM Script para restaurar las imágenes de static\backupImagenes a static\img

setlocal
set BACKUP_DIR=static\backupImagenes
set IMG_DIR=static\img

REM Eliminar el contenido actual de static\img
if exist "%IMG_DIR%" rmdir /s /q "%IMG_DIR%"

REM Copiar el backup a static\img
xcopy "%BACKUP_DIR%" "%IMG_DIR%" /E /I /Y

REM Si el backup se copió como subcarpeta, mover el contenido
if exist "%IMG_DIR%\backupImagenes" (
    xcopy "%IMG_DIR%\backupImagenes\*" "%IMG_DIR%" /E /I /Y
    rmdir /s /q "%IMG_DIR%\backupImagenes"
)

echo Imágenes restauradas desde backupImagenes a img.
endlocal 