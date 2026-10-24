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
| activo | BOOLEAN | Por defecto TRUE |
| multas_pendientes | INTEGER | Cantidad de multas sin pagar. Por defecto 0, nunca negativo |
| puede_rentar | BOOLEAN | **Calculada automáticamente**: TRUE solo si el usuario está activo y no tiene multas pendientes |
| creado_en | TIMESTAMP | Por defecto la fecha actual |

## Referencia desde otros servicios

Otros microservicios guardan este campo como `usuario_id` de tipo **BIGINT** (la cédula), sin llave foránea, porque cada servicio tiene su propia base.

## Datos de prueba

5 usuarios con cédulas ficticias (2 clientes, 2 vendedores, 1 admin). Contraseña de todos: `Test1234`.

María Gómez (`1023456789`) tiene 2 multas pendientes, así que `puede_rentar` es FALSE para ella. Sirve para probar el bloqueo.

## Verificar

    docker exec -it usuarios-db psql -U usuarios_user -d usuarios_db -c "SELECT id, nombre, multas_pendientes, puede_rentar FROM usuarios;"

## Reiniciar desde cero

Los scripts de `init/` solo corren cuando la base está vacía. Para volver a ejecutarlos:

    docker rm -f usuarios-db
    docker run -d --name usuarios-db -p 5432:5432 danionce/usuarios-db:1.0
