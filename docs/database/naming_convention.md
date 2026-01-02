# Database Naming Convention

## Table Names
- **Rule**: Table names MUST use `snake_case` (lowercase letters separated by underscores).
- **Format**: `lowercase_underscore`
- **Examples**:
    - Correct: `admin_user`, `ticket_order`, `user_profile`
    - Incorrect: `AdminUser`, `TP_Projects`, `TCG_Tickets`

## Column Names
- **Rule**: Column names SHOULD generally use `snake_case`.
- **Note**: Some legacy columns mapping to external systems (e.g. Lark) might currently deviate, but new columns should follow this.

## Migration Strategy
- When renaming existing tables:
    1. Update SQLAlchemy Models (`__tablename__`).
    2. Create migration script or manually rename in SQLite if needed (for this project, we might rely on `Base.metadata.create_all` which creates new tables, but data migration is key).
    3. Update all code references (Queries, Joins).
