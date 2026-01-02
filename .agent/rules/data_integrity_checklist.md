# Data Integrity & Flow Audit Checklist

To prevent missing data in Fullstack Features (like the "Missing Avatar in Redirect" issue), you **MUST** follow this audit trail when modifying data schemas:

## The "Hidden" Transport Layer Check
When data is passed between services via **Redirects** (e.g., OAuth Callbacks), it does **NOT** propagate automatically like a generic JSON object.

- [ ] **Controller Query Params**: If `res.redirect()` is used, are ALL new fields appended to the query string?
  - Example: `res.redirect('/login?token=...&name=' + name + '&avatar=' + avatar)`

## End-to-End Field Audit
When adding a new field (e.g., `avatar`):

1.  **DB Schema**: Added to Prisma/SQL Schema? Migration run?
2.  **Repository**: Fetched in the SELECT query?
3.  **Service**: Mapped to the Return DTO?
4.  **Controller (JSON)**: Included in `res.json()`?
5.  **Controller (Redirect)**: Appended to URL Query Params?
6.  **Frontend API**: Response Type updated?
7.  **Frontend State**: `localStorage` / Context parsing logic updated?
8.  **UI Component**: Component verifies valid data before rendering?

## Verification
- [ ] **Specific Scenario Test**: Do not just test "Login works". Test "Lark Login redirects AND carries the new data".
