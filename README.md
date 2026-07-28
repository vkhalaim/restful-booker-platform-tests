# restful-booker-platform-tests

An SDET-style test automation suite built against [restful-booker-platform](https://github.com/mwinteringham/restful-booker-platform) — a self-hosted booking system with a REST API and a web UI, purpose-built for practicing test automation.

The project demonstrates a full testing stack: API testing, UI testing, API+UI hybrid scenarios, load testing, and CI — rather than a single layer in isolation.

## Stack

- **Python 3.12**
- **Playwright** (sync API) — UI automation
- **pytest** + **pytest-rerunfailures** — test runner
- **requests** — API client layer
- **Locust** — load/performance testing
- **python-dotenv** — environment configuration
- **GitHub Actions** — CI (builds the platform from source and runs the full suite)

## Project structure

```
restful-booker-platform-tests/
├── api_clients/
│   ├── auth_client.py       # AuthApiClient: login, logout, validate
│   └── booking_client.py    # BookingApiClient: create/get/update/delete
├── pages/                   # Page Object Model
│   ├── admin_login_page.py
│   └── room_details_page.py
├── tests/
│   ├── api/                 # auth + booking API tests
│   ├── ui/                  # admin panel UI tests
│   ├── hybrid/              # API creates data, UI verifies it
│   └── perf/                # Locust load test scenarios
├── conftest.py              # shared fixtures (auth_token, created_booking)
├── requirements.txt
└── .github/workflows/tests.yml
```

## Architectural decisions

- **API client layer** wraps raw HTTP calls behind explicit methods (`login()`, `create_booking()`, etc.), with clear failure semantics: unexpected status codes raise `ValueError` with the response body attached, so failures are debuggable from the test output alone.
- **Page Object Model** for the UI, using role/label-based locators over brittle CSS where the markup allows it, with class-based locators reserved for cases where they were verified to be reliable.
- **Fixtures with teardown** (`auth_token`, `created_booking`) clean up their own state via `yield` + cleanup code, tolerant of the resource already being gone (e.g. deleted by the test itself).
- **Test data isolation**: booking dates and room assignments are randomized per test run to avoid collisions in a database that persists across runs (this platform does not reset itself between test executions).
- **`pytest-rerunfailures`** is used deliberately for tests whose failure mode can include rare, non-deterministic data collisions — not as a blanket flakiness suppressant.

## Setup

This suite tests a separately running instance of `restful-booker-platform`. Clone and build it per its own README (requires JDK 26, Maven 3.9.14, Node 24.14.1):

```bash
git clone https://github.com/mwinteringham/restful-booker-platform.git
cd restful-booker-platform
bash build_locally.sh
```

Then, in this repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

## Running tests

```bash
pytest tests/api tests/ui tests/hybrid -v
```

Load test (headless):
```bash
locust -f tests/perf/locustfile.py --host http://localhost:3000/booking --headless -u 5 -r 1 -t 30s
```

## CI

GitHub Actions builds `restful-booker-platform` from source (Java, Maven, Node), waits for all services to report healthy, then runs the full suite — API, UI, hybrid, and a short load test — against the freshly built instance. See `.github/workflows/tests.yml`.

## Platform bugs found during testing

Testing this platform surfaced several real discrepancies between its documented (Swagger) behavior and its actual behavior, each confirmed independently (via `curl`/a standalone diagnostic script) before being encoded as a test:

1. **Auth token delivery** — `POST /auth/login` returns the token via a `Set-Cookie` header, not in the JSON response body as the Swagger schema suggests.
2. **`PUT /booking/{id}` ignores `roomid`** — the endpoint accepts a new `roomid` in the request body but silently keeps the room assigned at creation time.
3. **`PUT /booking/{id}` self-conflicts on partial date overlap** — updating a booking to a date range that partially overlaps its own previous range fails with `409 Conflict`, as if it were conflicting with a different booking. A full, non-overlapping date shift succeeds.
4. **Admin UI booking row class collision** — each booking row on a room's admin detail page is rendered with a CSS class tied to the room ID rather than the booking ID or list index, so multiple bookings on the same room share an identical class — an unreliable basis for a locator.

## Known limitations / Future work

This suite intentionally prioritized depth over full surface coverage. Not yet covered:

- **Room service** — no tests for room creation/editing/deletion via the admin UI or API.
- **Message service** — the public contact form (which has `data-testid` attributes, unlike most of the public site) and its admin-side inbox are untested.
- **Branding service** — not explored.
- **Public booking flow** — the platform's primary user journey (browse rooms → pick dates → book → confirm on the public site) is untested; current coverage is limited to the admin panel and the API.
- **`GET /booking/unavailable` and `GET /booking/summary`** — not covered.

These were deliberately deprioritized in favor of a smaller number of well-architected, well-documented test paths (auth, booking CRUD, one admin screen, one hybrid scenario, and CI) rather than shallow coverage across the whole platform.