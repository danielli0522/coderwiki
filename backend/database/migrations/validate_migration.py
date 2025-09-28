#!/usr/bin/env python3
"""
Migration Validation Script for Repository Source Type Extensions
Validates that the database migration was applied correctly.
"""

import sys
import os
import pymysql
from typing import Dict, List, Tuple

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class MigrationValidator:
    """Validates database migration for repository source type extensions."""

    def __init__(self, host='localhost', user='root', password=None, database='coderwiki_dev'):
        """Initialize validator with database connection parameters."""
        self.host = host
        self.user = user
        self.password = password or input(f"Enter MySQL password for {user}: ")
        self.database = database
        self.connection = None

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            print(f"✓ Connected to database: {self.database}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to database: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def execute_query(self, query: str) -> List[Tuple]:
        """Execute a query and return results."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            return []

    def check_columns_exist(self) -> bool:
        """Check if the new columns exist in the repositories table."""
        print("\n1. Checking if new columns exist...")

        query = """
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = 'repositories'
          AND COLUMN_NAME IN ('source_type', 'local_source_path')
        ORDER BY COLUMN_NAME
        """

        results = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (self.database,))
                results = cursor.fetchall()
        except Exception as e:
            print(f"✗ Failed to check columns: {e}")
            return False

        expected_columns = {'source_type', 'local_source_path'}
        found_columns = {row[0] for row in results}

        if expected_columns.issubset(found_columns):
            print("✓ Required columns exist:")
            for row in results:
                column_name, column_type, is_nullable, default_value = row
                print(f"  - {column_name}: {column_type} (nullable: {is_nullable}, default: {default_value})")
            return True
        else:
            missing = expected_columns - found_columns
            print(f"✗ Missing columns: {missing}")
            return False

    def check_index_exists(self) -> bool:
        """Check if the source_type index exists."""
        print("\n2. Checking if source_type index exists...")

        query = """
        SHOW INDEX FROM repositories
        WHERE Key_name = 'idx_repositories_source_type'
        """

        results = self.execute_query(query)

        if results:
            print("✓ Index idx_repositories_source_type exists")
            for row in results:
                print(f"  - Column: {row[4]}, Index type: {row[10] if len(row) > 10 else 'N/A'}")
            return True
        else:
            print("✗ Index idx_repositories_source_type not found")
            return False

    def check_data_migration(self) -> bool:
        """Check if existing data was migrated correctly."""
        print("\n3. Checking data migration...")

        # Check total count and source_type distribution
        query = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN source_type = 'git_remote' THEN 1 ELSE 0 END) as git_remote_count,
            SUM(CASE WHEN source_type = 'local_output' THEN 1 ELSE 0 END) as local_output_count,
            SUM(CASE WHEN source_type IS NULL THEN 1 ELSE 0 END) as null_count
        FROM repositories
        """

        results = self.execute_query(query)

        if results:
            total, git_remote, local_output, null_count = results[0]
            print(f"✓ Repository count analysis:")
            print(f"  - Total repositories: {total}")
            print(f"  - Git remote repositories: {git_remote}")
            print(f"  - Local output repositories: {local_output}")
            print(f"  - NULL source_type (should be 0): {null_count}")

            if null_count == 0:
                print("✓ No NULL source_type values found (good)")
                return True
            else:
                print("✗ Found NULL source_type values (migration incomplete)")
                return False
        else:
            print("✗ Failed to retrieve repository data")
            return False

    def check_enum_values(self) -> bool:
        """Check if ENUM values are correctly defined."""
        print("\n4. Checking ENUM values...")

        query = """
        SELECT COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = 'repositories'
          AND COLUMN_NAME = 'source_type'
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (self.database,))
                result = cursor.fetchone()

                if result:
                    column_type = result[0]
                    print(f"✓ source_type column type: {column_type}")

                    # Check if it contains the expected values
                    if "'git_remote'" in column_type and "'local_output'" in column_type:
                        print("✓ ENUM contains expected values: git_remote, local_output")
                        return True
                    else:
                        print("✗ ENUM does not contain expected values")
                        return False
                else:
                    print("✗ Could not retrieve source_type column information")
                    return False
        except Exception as e:
            print(f"✗ Failed to check ENUM values: {e}")
            return False

    def check_foreign_keys(self) -> bool:
        """Check if foreign key constraints are still intact."""
        print("\n5. Checking foreign key constraints...")

        query = """
        SELECT
            CONSTRAINT_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = 'repositories'
          AND REFERENCED_TABLE_NAME IS NOT NULL
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (self.database,))
                results = cursor.fetchall()

                if results:
                    print("✓ Foreign key constraints found:")
                    for row in results:
                        constraint_name, column_name, ref_table, ref_column = row
                        print(f"  - {constraint_name}: {column_name} -> {ref_table}.{ref_column}")
                    return True
                else:
                    print("⚠ No foreign key constraints found (this might be expected)")
                    return True
        except Exception as e:
            print(f"✗ Failed to check foreign keys: {e}")
            return False

    def run_validation(self) -> bool:
        """Run all validation checks."""
        print(f"Repository Migration Validation")
        print(f"===============================")
        print(f"Database: {self.database}")
        print(f"Host: {self.host}")
        print(f"User: {self.user}")

        if not self.connect():
            return False

        try:
            checks = [
                self.check_columns_exist(),
                self.check_index_exists(),
                self.check_data_migration(),
                self.check_enum_values(),
                self.check_foreign_keys()
            ]

            passed = sum(checks)
            total = len(checks)

            print(f"\n" + "="*50)
            print(f"Validation Summary: {passed}/{total} checks passed")

            if passed == total:
                print("✓ Migration validation PASSED - All checks successful!")
                return True
            else:
                print("✗ Migration validation FAILED - Some checks failed!")
                return False

        finally:
            self.close()

def main():
    """Main function to run migration validation."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate Repository Migration')
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', help='MySQL password')
    parser.add_argument('--database', default='coderwiki_dev', help='Database name')

    args = parser.parse_args()

    validator = MigrationValidator(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()