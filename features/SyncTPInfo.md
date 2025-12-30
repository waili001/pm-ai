# Sync TP Info Requirements

## Goal
Synchronize additional fields for TP (Team Projects/Tickets) from Lark to the local database.

## Missing Fields
The following fields are currently missing or need to be ensured they are synchronized:
- **Released Date**: The date when the TP was released.
- **Description**: Detailed description of the TP.
- **Project Manager**: The PM in charge of the TP.
- **Due Day**: The due date for the TP.

## Technical Requirements
- Update Database Schema to include these columns.
- Update Sync Logic to map Lark fields to these columns.
- Ensure `Project Manager` is correctly mapped (verify Field Name).
