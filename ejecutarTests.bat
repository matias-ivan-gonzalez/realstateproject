@echo off
echo Ejecutando tests con coverage...
coverage run -m pytest
echo.
echo Mostrando reporte de coverage:
coverage report --include=backend\*.py
echo.
echo Generando reporte HTML...
coverage html --include=backend\*.py
echo El reporte HTML se generó en la carpeta "htmlcov".
pause
