@echo off
set PYTHONPATH=%cd%
echo Limpieza de datos de cobertura previos...
coverage erase
echo Ejecutando tests con pytest y coverage...
set PYTHONPATH=%cd%
coverage run --rcfile=.coveragerc --data-file=.coverage -m pytest --no-cov
if %ERRORLEVEL% NEQ 0 (
    echo Error: Los tests fallaron.
    pause
    exit /b 1
)
echo Verificando archivo de cobertura...
if not exist .coverage (
    echo Error: No se generó el archivo de cobertura.
    pause
    exit /b 1
)
echo Generando reporte de coverage...
coverage html
if %ERRORLEVEL% EQU 0 (
    echo El reporte HTML se ha generado en la carpeta 'htmlcov'.
    start htmlcov\index.html
) else (
    echo Error: No se pudo generar el reporte de coverage.
)
pause
