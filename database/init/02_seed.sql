-- ============================================================
-- Microservicio de Usuarios - Datos de prueba
-- Contraseña de todos los usuarios de prueba: Test1234
-- (se guarda cifrada con bcrypt, nunca en texto plano)
-- ============================================================

INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES
    ('Juan Pérez',      'juan@example.com',    crypt('Test1234', gen_salt('bf')), 'cliente'),
    ('María Gómez',     'maria@example.com',   crypt('Test1234', gen_salt('bf')), 'cliente'),
    ('Carlos Ramírez',  'carlos@example.com',  crypt('Test1234', gen_salt('bf')), 'vendedor'),
    ('Laura Torres',    'laura@example.com',   crypt('Test1234', gen_salt('bf')), 'vendedor'),
    ('Admin Sistema',   'admin@example.com',   crypt('Test1234', gen_salt('bf')), 'admin');
