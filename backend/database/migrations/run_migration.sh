#!/bin/bash
# Migration execution script for CoderWiki Database
# Usage: ./run_migration.sh [migration_file] [database_name]

set -e  # Exit on any error

# Configuration
DEFAULT_DB="coderwiki_dev"
MIGRATIONS_DIR="/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/backend/database/migrations"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check MySQL connection
check_mysql_connection() {
    if ! command -v mysql &> /dev/null; then
        print_error "MySQL client not found. Please install MySQL client."
        exit 1
    fi

    # Test connection (this will prompt for password if needed)
    if ! mysql -u root -p -e "SELECT 1;" > /dev/null 2>&1; then
        print_error "Cannot connect to MySQL. Please check your credentials."
        exit 1
    fi

    print_success "MySQL connection verified"
}

# Function to backup database before migration
backup_database() {
    local db_name=$1
    local backup_file="${db_name}_backup_$(date +%Y%m%d_%H%M%S).sql"

    print_status "Creating backup of database '$db_name'..."

    if mysqldump -u root -p "$db_name" > "$backup_file"; then
        print_success "Database backup created: $backup_file"
        echo "$backup_file"
    else
        print_error "Failed to create database backup"
        exit 1
    fi
}

# Function to run migration
run_migration() {
    local migration_file=$1
    local db_name=$2

    if [[ ! -f "$migration_file" ]]; then
        print_error "Migration file not found: $migration_file"
        exit 1
    fi

    print_status "Running migration: $(basename "$migration_file")"
    print_status "Target database: $db_name"

    # Show preview of what will be executed
    print_warning "Preview of migration (first 20 lines):"
    head -20 "$migration_file"
    echo ""

    # Confirm before proceeding
    read -p "Do you want to proceed with this migration? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Migration cancelled by user"
        exit 0
    fi

    # Run the migration
    if mysql -u root -p "$db_name" < "$migration_file"; then
        print_success "Migration completed successfully!"
    else
        print_error "Migration failed!"
        exit 1
    fi
}

# Function to list available migrations
list_migrations() {
    print_status "Available migrations in $MIGRATIONS_DIR:"
    if ls "$MIGRATIONS_DIR"/*.sql 2>/dev/null; then
        echo ""
    else
        print_warning "No migration files found"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -f, --file MIGRATION_FILE    Specific migration file to run"
    echo "  -d, --database DATABASE      Target database (default: $DEFAULT_DB)"
    echo "  -l, --list                   List available migrations"
    echo "  -b, --backup-only            Create backup only, don't run migration"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -f 001_add_repository_source_type_and_local_path.sql"
    echo "  $0 -f 001_add_repository_source_type_and_local_path.sql -d coderwiki"
    echo "  $0 -l"
    echo "  $0 -b -d coderwiki_dev"
}

# Parse command line arguments
MIGRATION_FILE=""
DATABASE="$DEFAULT_DB"
LIST_ONLY=false
BACKUP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            MIGRATION_FILE="$2"
            shift 2
            ;;
        -d|--database)
            DATABASE="$2"
            shift 2
            ;;
        -l|--list)
            LIST_ONLY=true
            shift
            ;;
        -b|--backup-only)
            BACKUP_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
print_status "CoderWiki Database Migration Tool"
print_status "=================================="

if [[ "$LIST_ONLY" == true ]]; then
    list_migrations
    exit 0
fi

# Check MySQL connection
check_mysql_connection

if [[ "$BACKUP_ONLY" == true ]]; then
    backup_database "$DATABASE"
    exit 0
fi

if [[ -z "$MIGRATION_FILE" ]]; then
    print_error "No migration file specified"
    list_migrations
    echo ""
    show_usage
    exit 1
fi

# Convert relative path to absolute if needed
if [[ ! "$MIGRATION_FILE" = /* ]]; then
    MIGRATION_FILE="$MIGRATIONS_DIR/$MIGRATION_FILE"
fi

# Create backup before migration
BACKUP_FILE=$(backup_database "$DATABASE")

# Run the migration
print_status "Starting migration process..."
run_migration "$MIGRATION_FILE" "$DATABASE"

print_success "Migration completed!"
print_status "Backup file: $BACKUP_FILE"
print_warning "Keep the backup file until you're sure the migration is working correctly"