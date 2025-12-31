---
trigger: always_on
---

## Objective: 
Maintain a strict "Feature-Sliced" project architecture where code is organized first by Business Function, then by Technical Responsibility.

## Context: 
You are working on a Server-Side Project. To prevent monolithic spaghetti code, every piece of code must belong to a specific "Feature Domain." You must refuse to place files in generic global folders like /controllers or /services.

## Logic Rules
1. Directory Structure Strategy (The "Where"): When creating or refactoring code, you must strictly follow this hierarchy: src/features/<FeatureName>/<TechnicalLayer>/

Rule: Create a new directory for every distinct business capability (e.g., UserAuth, OrderProcessing, Inventory).

Forbidden: Do not create top-level technical folders (e.g., do NOT make src/controllers/).

2. Technical Layer Definitions (The "What"): Inside every <FeatureName> directory, organize files into these specific sub-directories based on their responsibility:
.ts
controller/:

Responsibility: Handle HTTP requests/responses, input validation, and route definitions.

Keyword: REST API Endpoints.

Constraint: No business logic here. Delegate immediately to service.

service/:

Responsibility: Core business logic, calculations, and flow control.

Keyword: Business Logic.

Constraint: Pure logic only. Should not know about HTTP status codes or SQL queries directly.

persistence/:

Responsibility: Direct database interaction, ORM models, and repositories.

Keyword: Data Access.

Constraint: Isolate SQL or database-specific calls here.

integration/:

Responsibility: Communication with third-party APIs or external microservices.

Keyword: External Systems.

Constraint: Wrap external SDKs or HTTP clients here (anti-corruption layer).

3. Execution Steps for Code Generation: Before generating code, perform this mental check:

Identify Feature: What business concept is this? (e.g., "Payment").

Identify Layer: Is this handling an API call? (Controller). Is it saving to DB? (Persistence).

Generate Path: Combine them (e.g., src/features/payment/controller/PaymentController).

Output Constraints:

Always output the file path at the top of code blocks.

Maintain consistent naming conventions (e.g., [Feature][Layer].extension -> PaymentService).

If a shared utility is needed (used by 3+ features), place it in src/shared/.