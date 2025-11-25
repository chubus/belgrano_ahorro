-- Add image_url columns to negocios, sucursales, and productos tables

-- Add imagen column to negocios table if it doesn't exist
ALTER TABLE negocios ADD COLUMN IF NOT EXISTS imagen TEXT;

-- Add imagen column to sucursales table if it doesn't exist
ALTER TABLE sucursales ADD COLUMN IF NOT EXISTS imagen TEXT;

-- The productos table already has an 'imagen' column, so no need to add it
-- ALTER TABLE productos ADD COLUMN IF NOT EXISTS imagen TEXT;
