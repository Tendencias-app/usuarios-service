-- ============================================================
-- Microservicio de Usuarios - Datos de prueba
-- Las cédulas son FICTICIAS.
-- Contraseña de todos los usuarios de prueba: Test1234
-- (se guarda cifrada con bcrypt, nunca en texto plano)
-- ============================================================

INSERT INTO usuarios (id, nombre, email, password_hash, rol) VALUES
    (1012345678, 'Juan Pérez',      'juan@example.com',    crypt('Test1234', gen_salt('bf')), 'cliente'),
    (1023456789, 'María Gómez',     'maria@example.com',   crypt('Test1234', gen_salt('bf')), 'cliente'),
    (80123456,   'Carlos Ramírez',  'carlos@example.com',  crypt('Test1234', gen_salt('bf')), 'vendedor'),
    (52987654,   'Laura Torres',    'laura@example.com',   crypt('Test1234', gen_salt('bf')), 'vendedor'),
    (79456123,   'Admin Sistema',   'admin@example.com',   crypt('Test1234', gen_salt('bf')), 'admin');
