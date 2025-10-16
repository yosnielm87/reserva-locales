-- init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('admin','user');
CREATE TYPE reservation_status AS ENUM ('pending','approved','rejected','cancelled');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE locales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    capacity INTEGER,
    location VARCHAR(255),
    open_time TIME,
    close_time TIME,
    active BOOLEAN DEFAULT true
);

CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    locale_id UUID REFERENCES locales(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    start_dt TIMESTAMP NOT NULL,
    end_dt TIMESTAMP NOT NULL,
    motive TEXT,
    status reservation_status DEFAULT 'pending',
    priority INTEGER DEFAULT 9,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuario admin inicial: admin@admin.com / password: admin
INSERT INTO users (email, password_hash, full_name, role, is_active)
VALUES ('admin@admin.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrador', 'admin', true);

-- Locales de ejemplo
INSERT INTO locales (name, description, capacity, location, open_time, close_time, active)
VALUES
('Salón A', 'Salón de reuniones 1', 50, 'Piso 1', '08:00', '18:00', true),
('Cancha B', 'Cancha de fútbol 5', 22, 'Exterior', '07:00', '22:00', true);