-- Migration: 001_add_repository_source_type_and_local_path.sql
-- Description: Add source_type and local_source_path fields to repositories table
-- Date: 2025-09-28
-- Author: Database Administrator

-- ==============================================================================
-- FORWARD MIGRATION: Add new fields to repositories table
-- ==============================================================================

-- Check if we're running on the correct database
SELECT DATABASE() as current_database;

-- Start transaction to ensure atomicity
START TRANSACTION;

-- Add source_type column with ENUM type
-- Default to 'git_remote' for backward compatibility
ALTER TABLE repositories
ADD COLUMN source_type ENUM('git_remote', 'local_output')
DEFAULT 'git_remote'
NOT NULL
AFTER repo_metadata;

-- Add local_source_path column for storing local repository paths
-- VARCHAR(1000) to accommodate long file paths
-- Nullable since only local_output repositories will use this
ALTER TABLE repositories
ADD COLUMN local_source_path VARCHAR(1000)
NULL
AFTER source_type;

-- Add index on source_type for better query performance
CREATE INDEX idx_repositories_source_type ON repositories(source_type);

-- Update all existing repositories to have source_type = 'git_remote'
-- This ensures backward compatibility
UPDATE repositories
SET source_type = 'git_remote'
WHERE source_type IS NULL;

-- Verify the migration
SELECT
    COUNT(*) as total_repositories,
    SUM(CASE WHEN source_type = 'git_remote' THEN 1 ELSE 0 END) as git_remote_count,
    SUM(CASE WHEN source_type = 'local_output' THEN 1 ELSE 0 END) as local_output_count
FROM repositories;

-- Show updated table structure
DESCRIBE repositories;

-- Commit the transaction
COMMIT;

-- ==============================================================================
-- ROLLBACK INSTRUCTIONS (run these commands to reverse the migration)
-- ==============================================================================

/*
-- To rollback this migration, run the following commands:

START TRANSACTION;

-- Drop the index
DROP INDEX idx_repositories_source_type ON repositories;

-- Drop the new columns
ALTER TABLE repositories DROP COLUMN local_source_path;
ALTER TABLE repositories DROP COLUMN source_type;

-- Verify rollback
DESCRIBE repositories;

COMMIT;
*/

-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================

-- Verify that all existing repositories have source_type = 'git_remote'
SELECT
    id,
    name,
    source_type,
    local_source_path,
    url,
    created_at
FROM repositories
WHERE source_type != 'git_remote'
LIMIT 10;

-- Show sample of repositories with new fields
SELECT
    id,
    name,
    source_type,
    local_source_path,
    LEFT(url, 50) as url_preview,
    created_at
FROM repositories
ORDER BY created_at DESC
LIMIT 5;

-- Check index exists
SHOW INDEX FROM repositories WHERE Key_name = 'idx_repositories_source_type';