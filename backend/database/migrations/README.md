# Database Migrations

This directory contains database migration scripts for the CoderWiki application.

## Migration 001: Repository Source Type Extensions

### Overview
This migration adds support for local repositories from the `coderwiki-output-docs/repos/` directory by extending the Repository model with two new fields:

1. `source_type` - ENUM field to distinguish between Git remote and local repositories
2. `local_source_path` - VARCHAR field to store the path to local repositories

### Files
- `001_add_repository_source_type_and_local_path.sql` - Forward migration
- `001_rollback_repository_source_type_and_local_path.sql` - Rollback migration
- `run_migration.sh` - Migration execution script

### Schema Changes

#### New Columns Added to `repositories` table:

```sql
-- source_type: Identifies the type of repository source
source_type ENUM('git_remote', 'local_output') DEFAULT 'git_remote' NOT NULL

-- local_source_path: Path to local repository (nullable)
local_source_path VARCHAR(1000) NULL

-- Index for performance
INDEX idx_repositories_source_type (source_type)
```

### Backward Compatibility
- All existing repositories are automatically set to `source_type = 'git_remote'`
- No existing data is modified beyond adding the new fields
- The migration is fully reversible

### Running the Migration

#### Prerequisites
1. MySQL client installed and accessible
2. Database backup (automatically created by the script)
3. Appropriate database privileges

#### Execution

```bash
# Make the script executable (if not already)
chmod +x run_migration.sh

# List available migrations
./run_migration.sh -l

# Run the migration on development database
./run_migration.sh -f 001_add_repository_source_type_and_local_path.sql

# Run on specific database
./run_migration.sh -f 001_add_repository_source_type_and_local_path.sql -d coderwiki

# Create backup only
./run_migration.sh -b -d coderwiki_dev
```

#### Manual Execution
If you prefer to run the migration manually:

```bash
# Create backup first
mysqldump -u root -p coderwiki_dev > backup_before_migration.sql

# Run the migration
mysql -u root -p coderwiki_dev < 001_add_repository_source_type_and_local_path.sql
```

### Rollback

If you need to rollback the migration:

```bash
# Using the rollback script
./run_migration.sh -f 001_rollback_repository_source_type_and_local_path.sql

# Or manually
mysql -u root -p coderwiki_dev < 001_rollback_repository_source_type_and_local_path.sql
```

### Verification

After running the migration, verify the changes:

```sql
-- Check table structure
DESCRIBE repositories;

-- Verify data migration
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN source_type = 'git_remote' THEN 1 ELSE 0 END) as git_remote,
    SUM(CASE WHEN source_type = 'local_output' THEN 1 ELSE 0 END) as local_output
FROM repositories;

-- Check index exists
SHOW INDEX FROM repositories WHERE Key_name = 'idx_repositories_source_type';
```

### Application Integration

After running the migration, the Repository model in `/backend/app/models/repository.py` is already updated to support these fields:

```python
# New fields in Repository model
source_type = db.Column(db.Enum('git_remote', 'local_output'),
                       default='git_remote', nullable=False, index=True)
local_source_path = db.Column(db.String(1000))

# New methods
def is_local_repository(self) -> bool:
    return self.source_type == 'local_output'

def get_analysis_path(self) -> str:
    if self.source_type == 'local_output':
        return self.local_source_path
    else:
        return self.local_path
```

### Performance Considerations

1. **Index on source_type**: Added for efficient filtering by repository type
2. **VARCHAR(1000)**: Sufficient for most file paths while maintaining reasonable storage
3. **NULL local_source_path**: Only populated for local repositories to save space

### Security Considerations

1. **Path Validation**: Application code should validate local_source_path values
2. **Access Control**: Ensure proper permissions on local repository directories
3. **Backup**: Always backup before running migrations in production

### Monitoring and Alerting

After deployment, monitor:
- Migration execution time
- Database performance impact
- Application functionality with new fields
- Backup success and retention

### Disaster Recovery

1. **Backup Location**: Store backups in secure, separate location
2. **RTO/RPO**: Migration rollback typically takes < 5 minutes
3. **Testing**: Verify rollback procedure on development environment first

## Future Migrations

When adding new migrations:
1. Use sequential numbering: `002_`, `003_`, etc.
2. Include both forward and rollback scripts
3. Update this README with migration details
4. Test thoroughly on development environment