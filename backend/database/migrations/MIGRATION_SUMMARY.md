# Migration 001: Repository Source Type Extensions - Summary

## Overview
This migration extends the `repositories` table to support local repositories from the `coderwiki-output-docs/repos/` directory alongside existing Git remote repositories.

## Files Created

### 1. Migration Scripts
- **`001_add_repository_source_type_and_local_path.sql`**
  - Forward migration script
  - Adds `source_type` and `local_source_path` columns
  - Creates index for performance
  - Updates existing data for backward compatibility

- **`001_rollback_repository_source_type_and_local_path.sql`**
  - Rollback migration script
  - Removes the added columns and index
  - Fully reversible migration

### 2. Execution Tools
- **`run_migration.sh`**
  - Automated migration execution script
  - Includes backup creation, validation, and rollback support
  - Colored output and error handling

- **`validate_migration.py`**
  - Python script to validate migration success
  - Comprehensive checks for schema, data, and constraints
  - Detailed reporting of validation results

### 3. Documentation
- **`README.md`** - Comprehensive migration documentation
- **`MIGRATION_SUMMARY.md`** - This summary document

## Schema Changes

```sql
-- Added to repositories table:
source_type ENUM('git_remote', 'local_output') DEFAULT 'git_remote' NOT NULL
local_source_path VARCHAR(1000) NULL

-- Index added:
INDEX idx_repositories_source_type (source_type)
```

## Execution Steps

### 1. Pre-Migration Checklist
- [ ] Backup database
- [ ] Verify Repository model is updated (already done)
- [ ] Test on development environment
- [ ] Verify MySQL credentials and permissions

### 2. Run Migration
```bash
cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/backend/database/migrations

# List available migrations
./run_migration.sh -l

# Run the migration with automatic backup
./run_migration.sh -f 001_add_repository_source_type_and_local_path.sql

# For production database
./run_migration.sh -f 001_add_repository_source_type_and_local_path.sql -d coderwiki
```

### 3. Validate Migration
```bash
# Run validation script
./validate_migration.py --database coderwiki_dev

# Manual verification
mysql -u root -p coderwiki_dev -e "DESCRIBE repositories;"
```

### 4. Rollback (if needed)
```bash
./run_migration.sh -f 001_rollback_repository_source_type_and_local_path.sql
```

## Expected Results

### Database Schema
- `repositories` table has two new columns
- Index on `source_type` for performance
- All existing repositories have `source_type = 'git_remote'`
- Foreign key relationships remain intact

### Application Integration
The Repository model at `/backend/app/models/repository.py` already includes:
- New column definitions
- Helper methods for local repository support
- Updated `to_dict()` method
- Path resolution for analysis

## Verification Queries

```sql
-- Check table structure
DESCRIBE repositories;

-- Verify data migration
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN source_type = 'git_remote' THEN 1 ELSE 0 END) as git_remote,
    SUM(CASE WHEN source_type = 'local_output' THEN 1 ELSE 0 END) as local_output
FROM repositories;

-- Check index
SHOW INDEX FROM repositories WHERE Key_name = 'idx_repositories_source_type';
```

## Monitoring Recommendations

### Performance Metrics
- Migration execution time (expected: < 1 minute for small datasets)
- Query performance on repositories table
- Index usage for source_type filtering

### Data Integrity
- Verify no NULL values in source_type column
- Check foreign key constraints remain intact
- Validate application functionality with new fields

### Backup Strategy
- Keep pre-migration backup for at least 7 days
- Verify backup can be restored successfully
- Document backup location and retention policy

## Troubleshooting

### Common Issues
1. **Permission Errors**: Ensure MySQL user has ALTER privileges
2. **Connection Failures**: Verify MySQL service is running and credentials are correct
3. **Backup Failures**: Check disk space and write permissions
4. **Rollback Issues**: Use the dedicated rollback script, not manual commands

### Emergency Procedures
1. **Migration Fails**: Restore from backup and investigate
2. **Application Errors**: Check for code compatibility with new fields
3. **Performance Issues**: Monitor query execution plans and index usage

## Production Deployment

### Pre-Production
1. Test migration on staging environment
2. Verify application functionality
3. Document downtime window (expected: < 5 minutes)
4. Notify stakeholders of maintenance window

### Production Execution
1. Create production backup
2. Run migration during low-traffic period
3. Validate migration success
4. Monitor application logs for errors
5. Keep rollback plan ready

### Post-Production
1. Monitor performance metrics
2. Verify all application features work
3. Document lessons learned
4. Update monitoring dashboards

## Success Criteria

### Technical
- [ ] Migration executes without errors
- [ ] All validation checks pass
- [ ] Application starts without issues
- [ ] Query performance remains acceptable

### Functional
- [ ] Existing repositories continue to work
- [ ] New local repository support is available
- [ ] Analysis functionality works for both types
- [ ] User interface displays correctly

## Contact Information

For issues with this migration:
- Database Administrator: [Your contact info]
- Application Team: [Dev team contact]
- On-call Support: [Emergency contact]

## File Locations

All migration files are located in:
`/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/backend/database/migrations/`

- Forward migration: `001_add_repository_source_type_and_local_path.sql`
- Rollback migration: `001_rollback_repository_source_type_and_local_path.sql`
- Execution script: `run_migration.sh`
- Validation script: `validate_migration.py`
- Documentation: `README.md`, `MIGRATION_SUMMARY.md`