-- Tornar a coluna user_id nullable
ALTER TABLE extractions ALTER COLUMN user_id DROP NOT NULL;
