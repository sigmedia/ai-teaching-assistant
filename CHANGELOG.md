# Changelog

## 3.0.1 - 2026-02-15

### Fixed

### New Features
- Added new envronment varaible `REQUESTS_TIMEOUT_SECS`, enabling control over how long the web app will wait before assuming a query has timed out and responding with a placeholder apology.

## 2.0.1 - 2025-12-09

### Fixed
- Added missing `filelock` dependency to requirements.txt

## 2.0.0 - 2025-11-30

> Note: Always test migrations on a backup or staging environment first. Backup your data before running migrations on your production database.

### Breaking Changes
- New `ModifiedInputText` column required in messages table (see New Features)

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

- **Modified query capture** *(breaking)*: New `ModifiedInputText` column captures the modified user query (on the same row as its corresponding response message) when the Prompt Flow outputs a `modified_chat_input` field. Useful for tracking pre-processing changes to user queries.

**Migration:**
```sql
ALTER TABLE messages
ADD ModifiedInputText NVARCHAR(MAX) NULL;
```

### Improvements
- Better error handling in main chat flow

## 1.0.0 - 2025-11-25
- Initial release