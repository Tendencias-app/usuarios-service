# Imagen de la base de datos del microservicio de usuarios
FROM postgres:16-alpine

# Credenciales y nombre de la base (se pueden sobrescribir con -e al ejecutar)
ENV POSTGRES_DB=usuarios_db
ENV POSTGRES_USER=usuarios_user
ENV POSTGRES_PASSWORD=usuarios_pass

# Todo lo que esté en esta carpeta se ejecuta automáticamente, en orden
# alfabético, la PRIMERA vez que arranca el contenedor con volumen vacío
COPY init/ /docker-entrypoint-initdb.d/

EXPOSE 5432
