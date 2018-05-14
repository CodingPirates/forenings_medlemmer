#!/bin/bash

/usr/bin/sqlite3 /opt/database/db.sqlite3 ".dump" | bzip2 > /opt/database_backup/backup-$(date +%y-%m-%d-%H%M%S).sql.bz2

find /opt/database_backup -mtime +30 -exec rm {} \;

