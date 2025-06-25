@echo off
REM Script para restaurar las imágenes de static\backupImagenes a static\img

setlocal
set BACKUP_DIR=static\backupImagenes
set IMG_DIR=static\img

REM Eliminar el contenido actual de static\img
if exist "%IMG_DIR%" rmdir /s /q "%IMG_DIR%" >nul 2>&1

REM Copiar el backup a static\img
xcopy "%BACKUP_DIR%" "%IMG_DIR%" /E /I /Y >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se pudo restaurar las imagenes desde backupImagenes.
    endlocal
    exit /b 1
)

REM Si el backup se copio como subcarpeta, mover el contenido
if exist "%IMG_DIR%\backupImagenes" (
    xcopy "%IMG_DIR%\backupImagenes\*" "%IMG_DIR%" /E /I /Y >nul 2>&1
    rmdir /s /q "%IMG_DIR%\backupImagenes" >nul 2>&1
)

echo [OK] Imagenes restauradas desde backupImagenes a img.
endlocal 