@echo off
echo Ejecutando tests con pytest y coverage...
coverage run -m pytest  # Ejecuta los tests con coverage
if %ERRORLEVEL% NEQ 0 (
    echo "Error: Los tests fallaron."
    pause
    exit /b 1
)
echo Generando reporte de coverage...
coverage html  # Genera el reporte en formato HTML
if %ERRORLEVEL% EQU 0 (
    echo "El reporte HTML se ha generado en la carpeta 'htmlcov'."
    start htmlcov\index.html  # Abre el reporte automáticamente en tu navegador
) else (
    echo "Error: No se pudo generar el reporte de coverage."
)
pause