-- Schema: auth | Table: users

-- 1. Create schema auth
CREATE SCHEMA IF NOT EXISTS auth;

-- 2. Create enum userrole
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_type t
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typname = 'userrole' AND n.nspname = 'auth'
    ) THEN
        CREATE TYPE auth.userrole AS ENUM ('admin', 'customer');
    END IF;
END
$$;

-- 3. Create users table
CREATE TABLE IF NOT EXISTS auth.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    phone           BIGINT,
    role            auth.userrole NOT NULL DEFAULT 'customer',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    object_status   VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- 4. Seed admin account
INSERT INTO auth.users (
    id, name, email, hashed_password, phone, role, created_at, updated_at, object_status
)
VALUES (
    '019ff404-3f46-7c52-b499-7fe89d4ee129',
    'Anh Tuấn',
    'tuanbin2982003@gmail.com',
    '$2b$12$elhqeu/poRhjC0PrSba/..NZMNWF8we8bmWdqGI9PDLIuem.EcIIK',
    902570706,
    'admin',
    '2026-08-12 10:29:06.886654+07',
    '2026-08-12 10:31:12.624142+07',
    'active'
)
ON CONFLICT (email) DO NOTHING;
