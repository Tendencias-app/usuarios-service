"""Consumidor de eventos (Kafka) del microservicio de usuarios.

Eventos que CONSUME (este servicio no publica ninguno):
  - Usuario_usuarioActivado    -> usuarios.activo = TRUE
  - Usuario_usuarioDesactivado -> usuarios.activo = FALSE

Cada evento es un topic de Kafka con el mismo nombre. El valor del mensaje
es un JSON con la cédula del usuario, por ejemplo:
  {"usuario_id": 1012345678}
Si el valor no trae la cédula, se usa la clave (key) del mensaje.
"""
import json
import logging
import os
import threading
import time

from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic

import db

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")
log = logging.getLogger("usuarios.consumer")

EVENTO_ACTIVADO = os.getenv("EVENTO_ACTIVADO", "Usuario_usuarioActivado")
EVENTO_DESACTIVADO = os.getenv("EVENTO_DESACTIVADO", "Usuario_usuarioDesactivado")

# topic -> valor que toma la columna `activo`
EVENTOS = {EVENTO_ACTIVADO: True, EVENTO_DESACTIVADO: False}

# Claves aceptadas para la cédula dentro del JSON del evento
CLAVES_ID = ("usuario_id", "usuarioId", "id", "cedula")

_detener = threading.Event()
_hilo = None


def extraer_id(cuerpo) -> int:
    """Obtiene la cédula de un mensaje. Lanza ValueError/TypeError si no es válido."""
    datos = json.loads(cuerpo)
    if isinstance(datos, dict):
        for clave in CLAVES_ID:
            if clave in datos:
                return int(datos[clave])
    elif isinstance(datos, (int, str)):  # el cuerpo es solo la cédula
        return int(datos)
    raise ValueError(f"El evento no trae la cédula (se esperaba una de {CLAVES_ID})")


def extraer_cedula(valor, clave) -> int:
    """Busca la cédula en el valor del mensaje y, si no está, en su clave."""
    try:
        return extraer_id(valor)
    except (ValueError, TypeError):
        if clave:
            return extraer_id(clave)
        raise


def procesar_mensaje(consumidor, msg) -> None:
    """Aplica un evento a la base de datos y confirma (commit) el mensaje."""
    evento = msg.topic()
    activo = EVENTOS[evento]

    try:
        usuario_id = extraer_cedula(msg.value(), msg.key())
    except (ValueError, TypeError) as error:
        # Mensaje mal formado: reintentar no sirve, se descarta
        log.error("[%s] Mensaje inválido descartado (%s): %r", evento, error, msg.value())
        consumidor.commit(message=msg, asynchronous=False)
        return

    try:
        existe = db.cambiar_estado(usuario_id, activo)
    except Exception:
        # Falla temporal (por ejemplo la BD no responde): NO se confirma el mensaje
        # y se vuelve a su posición para reintentarlo
        log.exception("[%s] Error de base de datos, se reintentará", evento)
        consumidor.seek(TopicPartition(msg.topic(), msg.partition(), msg.offset()))
        time.sleep(5)
        return

    if existe:
        log.info("[%s] Usuario %s -> activo=%s", evento, usuario_id, activo)
    else:
        log.warning("[%s] Usuario %s no existe, evento ignorado", evento, usuario_id)
    consumidor.commit(message=msg, asynchronous=False)


def _crear_topics(servidores: str) -> None:
    """Crea los topics si no existen (si ya existen, no hace nada)."""
    admin = AdminClient({"bootstrap.servers": servidores})
    nuevos = [NewTopic(nombre, num_partitions=1, replication_factor=1) for nombre in EVENTOS]
    for nombre, futuro in admin.create_topics(nuevos, request_timeout=10).items():
        try:
            futuro.result()
            log.info("Topic creado: %s", nombre)
        except KafkaException as error:
            if error.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                raise


def _bucle(servidores: str) -> None:
    """Mantiene el consumidor activo; si algo falla, reintenta cada 5 segundos."""
    while not _detener.is_set():
        consumidor = None
        try:
            _crear_topics(servidores)
            consumidor = Consumer({
                "bootstrap.servers": servidores,
                "group.id": os.getenv("KAFKA_GROUP_ID", "usuarios-service"),
                "auto.offset.reset": "earliest",   # si el grupo es nuevo, lee desde el inicio
                "enable.auto.commit": False,       # se confirma a mano, después de guardar en la BD
            })
            consumidor.subscribe(list(EVENTOS))
            log.info("Escuchando eventos: %s", ", ".join(EVENTOS))
            while not _detener.is_set():
                msg = consumidor.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().fatal():
                        raise KafkaException(msg.error())
                    log.warning("Kafka: %s", msg.error())
                    continue
                procesar_mensaje(consumidor, msg)
        except Exception as error:
            log.warning("Problema con Kafka (%s). Reintentando en 5 s...", error)
            _detener.wait(5)
        finally:
            if consumidor is not None:
                try:
                    consumidor.close()
                except Exception:
                    pass


def iniciar() -> None:
    """Arranca el consumidor en un hilo. Si KAFKA_BOOTSTRAP_SERVERS no está definida, no hace nada."""
    global _hilo
    servidores = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not servidores:
        log.info("KAFKA_BOOTSTRAP_SERVERS no definida: consumidor de eventos deshabilitado")
        return
    _detener.clear()
    _hilo = threading.Thread(target=_bucle, args=(servidores,), daemon=True, name="consumidor-eventos")
    _hilo.start()


def detener() -> None:
    _detener.set()
    if _hilo is not None:
        _hilo.join(timeout=10)
