-- ============================================================
-- Microservicio de Usuarios - Creación de tablas
-- ============================================================

-- Permite cifrar contraseñas con bcrypt (crypt / gen_salt)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS usuarios (
    id             SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    rol            VARCHAR(30)  NOT NULL DEFAULT 'cliente',
    activo         BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en      TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_usuarios_rol CHECK (rol IN ('cliente', 'vendedor', 'admin'))
);

CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios (rol);
