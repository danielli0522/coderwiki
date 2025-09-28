-- Rollback Migration: 001_rollback_repository_source_type_and_local_path.sql
-- Description: Rollback the addition of source_type and local_source_path fields
-- Date: 2025-09-28
-- Author: Database Administrator

-- ==============================================================================
-- ROLLBACK MIGRATION: Remove source_type and local_source_path from repositories
-- ==============================================================================

-- Check if we're running on the correct database
SELECT DATABASE() as current_database;

-- Show current table structure before rollback
DESCRIBE repositories;

-- Show current data to verify what we're removing
SELECT
    COUNT(*) as total_repositories,
    SUM(CASE WHEN source_type = 'git_remote' THEN 1 ELSE 0 END) as git_remote_count,
    SUM(CASE WHEN source_type = 'local_output' THEN 1 ELSE 0 END) as local_output_count
FROM repositories;

-- Warning: Check for local_output repositories before rollback
SELECT
    id,
    name,
    source_type,
    local_source_path
FROM repositories
WHERE source_type = 'local_output';

-- Start transaction to ensure atomicity
START TRANSACTION;

-- Drop the index first
DROP INDEX IF EXISTS idx_repositories_source_type ON repositories;

-- Drop the local_source_path column
ALTER TABLE repositories DROP COLUMN IF EXISTS local_source_path;

-- Drop the source_type column
ALTER TABLE repositories DROP COLUMN IF EXISTS source_type;

-- Verify the rollback
DESCRIBE repositories;

-- Show sample data to confirm columns are removed
SELECT
    id,
    name,
    url,
    created_at
FROM repositories
ORDER BY created_at DESC
LIMIT 5;

-- Commit the transaction
COMMIT;

-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================

-- Verify columns no longer exist
SELECT
    COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'repositories'
  AND COLUMN_NAME IN ('source_type', 'local_source_path');

-- This should return no rows if rollback was successful

-- Show final table structure
SHOW CREATE TABLE repositories;