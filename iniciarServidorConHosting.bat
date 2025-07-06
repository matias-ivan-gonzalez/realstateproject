@echo off
REM Detecta el usuario de Windows y asigna el dominio correspondiente
set "DOMINIO="

if /I "%USERNAME%"=="COMPUMAR"  set "DOMINIO=sparrow-popular-lovely.ngrok-free.app"
if /I "%USERNAME%"=="feliu"  set "DOMINIO=sparrow-popular-lovely.ngrok-free.app"
if /I "%USERNAME%"=="ASUS"      set "DOMINIO=relevant-thoroughly-kiwi.ngrok-free.app"
if /I "%USERNAME%"=="masud"     set "DOMINIO=devoted-up-ocelot.ngrok-free.app"
if /I "%USERNAME%"=="Matia"     set "DOMINIO=liked-indirectly-finch.ngrok-free.app"

if "%DOMINIO%"=="" (
    echo Usuario no reconocido. Por favor, configura tu dominio en el script.
    pause
    exit /b
)

REM Define la variable de entorno BASE_URL para el backend
set BASE_URL=https://%DOMINIO%

REM Levanta el servidor en el puerto 5000 en una nueva ventana
start "" iniciarServidor.bat

REM Espera 5 segundos para asegurarse de que el servidor esté arriba
timeout /t 5

REM Ejecuta ngrok con el dominio correspondiente
ngrok http --url %DOMINIO% 5000

pause
