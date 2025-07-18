# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
python runserver.py
```
The application runs on `localhost:8000` by default.

### Testing
```bash
pytest                    # Run all tests
pytest tests/             # Run specific test directory
pytest -v                 # Verbose output
pytest --cov              # Run with coverage
```

### Code Quality
```bash
black .                   # Format code
mypy .                    # Type checking
```

### Database Operations
```bash
flask database create-tables    # Create all database tables
flask database clear-data       # Clear all data from tables
flask database test-data        # Create test data for development
flask db migrate -m "message"   # Create migration
flask db upgrade                # Apply migrations
```

## Architecture Overview

This is a **Flask expense-sharing web application** similar to Splitwise, built with a modular blueprint structure.

### Core Framework Stack
- **Flask** with SQLAlchemy ORM and Flask-Migrate for database management
- **SQLite** database with Alembic migrations
- **Flask-Login** for user authentication
- **WTForms** for form handling and validation
- **Jinja2** templates for frontend rendering

### Application Structure
The app follows a **blueprint-based modular architecture**:

- **`app/`** - Main application package
  - **`auth/`** - User authentication (login, registration, logout)
  - **`user/`** - User management (friends, dashboard, profile)
  - **`group/`** - Group management (create groups, manage members)
  - **`expense/`** - Expense tracking and management
  - **`debt/`** - Debt calculation and settlement logic
  - **`split/`** - Expense splitting algorithms (equally, by amount, by percentage)
  - **`model/`** - SQLAlchemy database models
  - **`templates/`** - Jinja2 HTML templates organized by feature

### Key Domain Models
- **User**: Manages user accounts, friends relationships, authentication
- **Group**: Expense sharing groups with multiple users
- **Expense**: Tracks expenses with flexible splitting options
- **Balance**: Records individual user balances for each expense
- **Debt**: Calculates and tracks money owed between users

### Expense Splitting System
The application supports three splitting methods:
- **Equally**: Split evenly among participants
- **By Amount**: Custom amounts per person
- **By Percentage**: Percentage-based splitting

Split logic is handled in `app/split/` with separate modules for each method.

### Database Design
- Uses SQLAlchemy with declarative base and proper foreign key relationships
- Alembic migrations for schema changes
- Association tables for many-to-many relationships (friends, group members, expense participants)

### Configuration
- Environment-specific configs in `app/config.py` (Development, Test, Production)
- Database CLI commands for setup and test data generation
- MyPy configuration for type checking

### Testing Strategy
- Pytest-based test suite with fixtures and conftest files
- Organized by feature modules matching the application structure
- Comprehensive model and view testing