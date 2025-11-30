# Changelog

## 2.0.0 - 2025-11-30

> Note: Always test migrations on a backup or staging environment first. Backup your data before running migrations on your production database.

### Breaking Changes
- New column added to messages database table

**Migration:**
```sql
ALTER TABLE messages
ADD ModifiedInputText NVARCHAR(MAX) NULL;
```

### New Features
- Application runs on Windows OS
- International languages support (requires changes to the messages database table)

**Migration:**
```sql
ALTER TABLE sessions
ALTER COLUMN AgreementPart1Version NVARCHAR(64) NOT NULL;

ALTER TABLE sessions
ALTER COLUMN AgreementPart2Version NVARCHAR(64) NOT NULL;

ALTER TABLE messages
ALTER COLUMN MessageText NVARCHAR(MAX) NULL;
```

### Improvements
- Better error handling in main chat flow

## 1.0.0 - 2025-11-25
- Initial release