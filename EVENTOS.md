# Eventos del microservicio de Usuarios (Kafka)

Este servicio **solo consume** eventos; no publica ninguno.

| Evento | Topic | Efecto en la tabla `usuarios` |
|---|---|---|
| `Usuario_usuarioActivado` | `Usuario_usuarioActivado` | `activo = TRUE` |
| `Usuario_usuarioDesactivado` | `Usuario_usuarioDesactivado` | `activo = FALSE` |

Grupo de consumidores: `usuarios-service`.

## Formato del mensaje

El **valor** es un JSON con la cédula del usuario:

    {"usuario_id": 1012345678}

También se acepta la cédula en las claves `usuarioId`, `id` o `cedula`, o el valor con solo el número.
Si el valor no trae la cédula, se usa la **clave (key)** del mensaje.

## Comportamiento

- Si el usuario **no existe**, el evento se ignora (queda en el log).
- Si el mensaje está **mal formado**, se descarta y se registra el error.
- Si la base de datos falla, el mensaje **no se confirma** y se reintenta.
- El mensaje se confirma (commit) solo después de guardar en la base de datos.
- Procesar el mismo evento dos veces deja el mismo resultado (es idempotente).
- Los topics se crean solos al arrancar si no existen (1 partición).

## Configuración (variables de entorno)

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | (vacía: consumidor deshabilitado) | Por ejemplo `kafka:19092` |
| `KAFKA_GROUP_ID` | `usuarios-service` | Grupo de consumidores |
| `DATABASE_URL` | `postgresql://usuarios_user:usuarios_pass@localhost:5432/usuarios_db` | Conexión a PostgreSQL |
| `EVENTO_ACTIVADO` | `Usuario_usuarioActivado` | Nombre del topic |
| `EVENTO_DESACTIVADO` | `Usuario_usuarioDesactivado` | Nombre del topic |

## Probar

    docker compose up --build

**Con el panel web** (http://localhost:8080):
1. **Topics → `Usuario_usuarioDesactivado` → Produce Message**.
2. En *Value* escribe `{"usuario_id": 1012345678}` y pulsa **Produce Message**.
3. En http://localhost:8000/docs ejecuta `GET /usuarios/1012345678/estado`: debe decir `activo: false`.
4. Repite con el topic `Usuario_usuarioActivado` y debe volver a `true`.

**Con la terminal** (alternativa):

    docker compose exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic Usuario_usuarioDesactivado

Escribe `{"usuario_id": 1012345678}`, pulsa Enter y luego `Ctrl + C`.
