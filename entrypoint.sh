#!/bin/sh

# Command to execute the latest migration version 
poetry run alembic upgrade head

# Run the FastAPI project
poetry run uvicorn fin_control.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload