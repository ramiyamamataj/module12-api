# Module 12: User Authentication and Calculation BREAD REST API

## Overview
FastAPI web service providing user registration and JWT login endpoints alongside authenticated BREAD (Browse, Read, Edit, Add, Delete) routes for polymorphic arithmetic calculations backed by PostgreSQL and SQLAlchemy.

## API Endpoints
- `GET /health` - Service health status
- `POST /users/register` - Register a new user account
- `POST /users/login` - Authenticate with JSON credentials and receive a JWT access token
- `POST /users/token` - OAuth2 form authentication for OpenAPI Swagger UI authorization
- `POST /calculations` - Create a new calculation (`add`, `sub`, `multiply`, `divide`)
- `GET /calculations` - List all calculations belonging to the authenticated user
- `GET /calculations/{id}` - Retrieve a single calculation by UUID
- `PUT /calculations/{id}` - Update calculation type or inputs and recompute result
- `DELETE /calculations/{id}` - Delete a calculation record

## Docker Hub Repository
- **Docker Hub Image:** https://hub.docker.com/r/ramiyamamataj/module12-api

## Running Locally & Executing Tests
1. Start the PostgreSQL, FastAPI, and pgAdmin containers:
   ```bash
   docker compose up -d --build
   ```
2. Activate the virtual environment and run the test suite:
   ```bash
   source venv/bin/activate
   pytest -v --cov=app --cov-report=term-missing
   ```
3. Open `http://localhost:8000/docs` in your browser to test user registration, authorize via OAuth2, and run calculation BREAD requests through Swagger UI.
