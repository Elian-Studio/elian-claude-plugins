# Login Example

Example feature: email/password login for an existing web application.

## Phase 1: Feature Framing

Intent: let registered users authenticate with email and password while protecting accounts from brute force and preserving clear failure handling.

Users:

- Registered user.
- Admin/support user who may diagnose login failures.

Success criteria:

- Valid credentials create a session.
- Invalid credentials do not reveal whether the email exists.
- Locked or disabled accounts cannot log in.
- Session and refresh behavior follows existing auth policy.

Must not fail:

- Do not log passwords.
- Do not weaken existing session expiry.
- Do not introduce account enumeration.
- Do not bypass MFA if the product already requires it.

Risk: high because it touches authentication, session state, privacy, and abuse prevention.

Open questions:

- Is MFA in scope?
- What lockout threshold is approved?
- What error copy is acceptable?
- Which session storage is canonical?

## Phase 2: BDD

```gherkin
Feature: Email/password login

Scenario: Valid credentials create a session
  Given a registered active user
  When the user submits the correct email and password
  Then a session is created
  And the user is redirected to the default signed-in page

Scenario: Wrong password returns a generic error
  Given a registered active user
  When the user submits a wrong password
  Then no session is created
  And the response does not reveal whether the email exists

Scenario: Locked account cannot log in
  Given a locked account
  When correct credentials are submitted
  Then no session is created
  And the user sees the approved locked-account message
```

## Phase 3: SDD

Scope:

- Login form validation.
- Credential verification.
- Session creation.
- Generic error response.
- Lockout/disabled-account handling.
- Tests for auth success and failure.

Out of scope:

- Registration.
- Password reset.
- MFA enrollment unless explicitly added.
- Broad auth refactor.

Acceptance criteria:

- Email and password are required.
- Password verification uses the existing password hashing service.
- Error responses do not leak account existence.
- Existing session expiry behavior is preserved.
- Audit/logging records failure without secrets.

## Phase 4: DDD

DDD is useful at a light level because authentication has policy and invariants.

Possible model:

- Entity: `UserAccount`.
- Value objects: `EmailAddress`, `PasswordHash`.
- Domain service: `CredentialVerifier`.
- Policy: `AccountLockPolicy`.
- Repository: existing user/account repository.
- Invariant: locked and disabled accounts cannot create sessions.

Avoid:

- Creating a full new auth bounded context if the application already has one.
- Moving unrelated profile logic.

## Phase 5: AI-TDD

Required tests:

- Valid credentials create session.
- Wrong password returns generic error.
- Unknown email returns the same generic error shape.
- Locked account cannot create session.
- Disabled account cannot create session.
- Password value is never logged.
- Existing session expiry tests still pass.

Protected tests:

- Existing auth expiry tests.
- Existing MFA tests when MFA exists.
- Existing tenant or account isolation tests.

## Phase 6: Context Engineering

Required context:

- Existing auth controller or route.
- User/account model.
- Password hashing/verification service.
- Session creation service.
- Auth tests.
- Error copy or i18n files.

No-touch:

- Registration flow.
- Password reset.
- MFA policy unless included in scope.
- Global session expiry policy unless explicitly changed.

## Phase 7: Agentic Coding Ticket

```text
# Task: Email/password login
## Goal
Implement email/password login using the existing auth stack.

## Scope
Login form, credential verification, session creation, generic failure handling, tests.

## Out of Scope
Registration, password reset, MFA enrollment, unrelated auth refactor.

## Acceptance Criteria
See SDD acceptance criteria and AI-TDD tests.

## Required Context
Read the listed auth routes, account model, password service, session service, and auth tests.

## Constraints
Do not log secrets. Do not change protected tests except to strengthen them.

## Test Requirements
Run auth unit tests and relevant integration tests.
```

## Phase 8: Review

Block merge if:

- Error response leaks account existence.
- Locked/disabled account creates a session.
- Passwords or hashes are logged.
- Existing expiry/MFA behavior changes without spec.
- Failure-path tests are missing.

## Phase 9: SPDD Archive

Archive:

- The generic error policy.
- Lockout policy decision.
- Required auth context files.
- Protected tests.
- Any product-policy questions not resolved.
