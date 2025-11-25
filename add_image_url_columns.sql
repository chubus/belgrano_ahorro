-- Script para agregar campo image_url a las tablas que no lo tienen
-- Ejecutar este script en la base de datos PostgreSQL

-- Agregar image_url a negocios si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'negocios' AND column_name = 'image_url'
    ) THEN
        ALTER TABLE negocios ADD COLUMN image_url TEXT;
    END IF;
END $$;

-- Agregar image_url a sucursales si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sucursales' AND column_name = 'image_url'
    ) THEN
        ALTER TABLE sucursales ADD COLUMN image_url TEXT;
    END IF;
END $$;

-- Los productos ya tienen campo 'imagen', pero agregamos 'image_url' para consistencia
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'productos' AND column_name = 'image_url'
    ) THEN
        ALTER TABLE productos ADD COLUMN image_url TEXT;
    END IF;
END $$;

