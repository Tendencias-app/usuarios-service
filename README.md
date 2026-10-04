# Microservicio de Usuarios

API REST para la gestión de usuarios (CRUD completo), desarrollada con FastAPI.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | /usuarios | Lista los usuarios |
| GET | /usuarios/{id} | Consulta un usuario por ID |
| POST | /usuarios | Crea un usuario |
| PUT | /usuarios/{id} | Actualiza un usuario |
| DELETE | /usuarios/{id} | Elimina un usuario |

## Ejecutar con Docker

    docker run -p 8000:8000 danionce/usuarios-service:1.0

Documentación Swagger: http://localhost:8000/docs

## Imagen en Docker Hub

`danionce/usuarios-service:1.0`

## Tecnologías

Python 3.10 · FastAPI · Uvicorn · Pydantic · Docker
