# Python Project Rules

## 1. Formatting

- Use `ruff check .`
- Use `ruff format .`

## 2. Project Structure

``` text
app/
    api/
    core/
    db/
    models/
    repository/
    services/
    routers/
    schemas/
    utils/
    configs/
```

- Routers call Services only, no business logic inside routers, define request/response_model for each API.
- Service contains business logic.
- Repository only accesses the database.
- Models define ORM entities.
- Schemas define request/response models.
- Utils must not contain business logic.

## 3. Database

- Repository never commits.
- Commit only in UnitOfWork or Service.

## 4. Transactions

- One business operation = one transaction.

## 5. Configuration

- No hardcoded configuration.
- Read values from config/environment.

## 6. Service

- Independent from HTTP layer.

## 7. Repository

- CRUD and queries only.
- No validation, cache, permission checks, or external API calls.

## 8. Logging

- Use logger.info(), logger.warning(), logger.error(), logger.exception().

## 9. Transactions

- One business operation = one transaction.