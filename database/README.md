# Base de datos - Microservicio de Usuarios

Imagen de PostgreSQL 16 con el esquema y datos de prueba del microservicio de usuarios.

## Imagen en Docker Hub

`danionce/usuarios-db:1.0`

## Ejecutar

    docker run -d --name usuarios-db -p 5432:5432 danionce/usuarios-db:1.0

## Conexión

| Dato | Valor |
|---|---|
| Host | localhost |
| Puerto | 5432 |
| Base de datos | usuarios_db |
| Usuario | usuarios_user |
| Contraseña | usuarios_pass |

URL de conexión: `postgresql://usuarios_user:usuarios_pass@localhost:5432/usuarios_db`

## Tabla `usuarios`

| Columna | Tipo | Notas |
|---|---|---|
| id | BIGINT | Clave primaria. **Es el número de cédula**; lo envía el cliente, no se autogenera. Entre 1 y 9999999999 |
| nombre | VARCHAR(100) | Obligatorio |
| email | VARCHAR(150) | Obligatorio, único |
| password_hash | VARCHAR(255) | Contraseña cifrada (bcrypt) |
| rol | VARCHAR(30) | cliente (por defecto), vendedor o admin |
| activo | BOOLEAN | Por defecto TRUE. **Lo modifican los eventos** `Usuario_usuarioActivado` (TRUE) y `Usuario_usuarioDesactivado` (FALSE) |
| creado_en | TIMESTAMP | Por defecto la fecha actual |

## Referencia desde otros servicios

Otros microservicios guardan este campo como `usuario_id` de tipo **BIGINT** (la cédula), sin llave foránea, porque cada servicio tiene su propia base.

## Datos de prueba

5 usuarios con cédulas ficticias (2 clientes, 2 vendedores, 1 admin), todos activos. Contraseña de todos: `Test1234`.

## Verificar

    docker exec -it usuarios-db psql -U usuarios_user -d usuarios_db -c "SELECT id, nombre, activo FROM usuarios;"

## Reiniciar desde cero

Los scripts de `init/` solo corren cuando la base está vacía. Para volver a ejecutarlos:

    docker rm -f usuarios-db
    docker run -d --name usuarios-db -p 5432:5432 danionce/usuarios-db:1.0
