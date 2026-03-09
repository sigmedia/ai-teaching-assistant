# Changelog

## 3.0.1 - 2026-03-09

### Fixed
- Fixed input validation bug where validated boolean results overwrote original login data values
- Fixed `validate_chat_message` returning `True` instead of the validated message string
- Fixed missing `@staticmethod` decorators on `validate_login_data` and `validate_chat_message`
- Fixed failed chat validation (empty or over-length messages) falling through to the API instead of returning an error to the user
- Fixed typo in validation error message

### Security
- Added HTML sanitization of bot output to protect against cross-site scripting (XSS)
- Added SECURITY.md with vulnerability reporting and deployer responsibility guidelines

### Improvements
- Updated README.md and SECURITY.md with deployer liability notice and LICENSE links

## 3.0.0 - 2026-02-15

### Fixed
- Issue with markdown causing broken code display under specific conditions
- Issue with markdown causing broken Latex math display when the math is presented in a table

### New Features
- Added new environment varaible `REQUEST_TIMEOUT_SECS`, enabling control over how long the web app will wait before assuming a query has timed out and responding with a placeholder apology
- Included further supplementary material and reproducibility instructions pertaining to MPE Deployment 2025. See [tools/evaluation/other-data/mpe-experiment-2025](tools/evaluation/other-data/mpe-experiment-2025).
- Updated [README.md](README.md) to with deployment instructions adjusted to work with recent changes to Azure's Web App github workflow, as well as information about the new environment variable, how to configure the Azure Web App so it doesn't idle out on inactivity, and the additional supplementariy materials.

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
