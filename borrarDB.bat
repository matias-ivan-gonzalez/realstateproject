@echo off
if exist backend\mydatabase.db (
    del backend\mydatabase.db
    echo Base de datos borrada.
) else (
    echo No se encontró la base de datos.
)