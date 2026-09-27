# Testing

## Verified Results

On the latest verified execution:

**Backend (`python -m pytest`)**:
- 71 tests passed.
- 0 failed.
- 0 skipped.
- 11 warnings reported (e.g., SQLAlchemy isolation-option warnings, pytest-asyncio deprecations).

**Frontend**:
- `npm run build`: Succeeded.
- `npm run lint`: Exited successfully (1 existing warning remains in `src/pages/BookingPage.jsx` for an unused catch parameter).

## Test Coverage Areas

| Area | Evidence |
|---|---|
| **Unit / Service** | Timezone parsing, parent normalization, email dispatching, course filtering, admin analytics, and core booking-service modules are comprehensively covered. |
| **API layer** | Admin and course tests extensively utilize the FastAPI `TestClient` to verify HTTP inputs, parameter mapping, and response models. |
| **Booking / Allocation** | Verifies valid and invalid course rejection, parent creation, active mentor filtering, deterministic assignment integrity, and the strict unique mentor-slot conflict constraint. |
| **Timezone / DST** | Covers UTC to IST conversion, IANA identifier validation, US EST/EDT offset boundary shifts, UK GMT/BST handling, and forward date-window boundaries. |
| **Concurrency** | The transaction retry handling logic is verified. *(Note: A dedicated concurrent multi-request stress test over the wire is not included in the standard suite).* |
| **Email** | Validates internal formatting, dual-recipient preparation, console-simulation dispatching, SMTP configuration presence checks, commit-before-notification logic, post-commit failure resilience, and staff resend overrides. |
| **Admin Operations** | Confirms capacity metrics calculations, mentor lifecycle updates (create/edit/activation), course CRUD, parent history tracking, and booking visibility. |
| **Frontend** | Lint and Vite production builds are validated. *(Note: No automated Puppeteer/Cypress browser interaction suite is present in this implementation).* |

## Edge Case Handling

Crucial edge cases actively covered by the test suite include:
- Rejection of invalid IANA timezones.
- Rejection of malformed, stale, or non-aligned booking slots.
- Enforcement of past and future date-window boundaries.
- Database prevention of exact mentor-slot overlap conflicts.
- Adherence to the two-class per IST calendar day maximum capacity limitation.
- Graceful `409 Conflict` generation when absolutely no mentor is available.
- Proper fallback when post-commit SMTP email delivery fails (retaining the booking integrity).
