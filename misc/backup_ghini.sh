#!/bin/bash

# Variables
HOST="postgres.wysechoice.net"
PORT="5432"
DB_NAME="ghini_test2"
USER="ghini"
BACKUP_DIR="$HOME/db_backups/ghini_full_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ghini_test2_full_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform the backup using pg_dump (Plain SQL format)
pg_dump \
  -h "$HOST" \
  -p "$PORT" \
  -U "$USER" \
  -d "$DB_NAME" \
  -F p \
  -f "$BACKUP_FILE"

# Optional: Remove backups older than 30 days
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +30 -exec rm {} \;

# Log the backup
echo "Backup completed successfully at $TIMESTAMP." >> "$BACKUP_DIR/backup.log"
