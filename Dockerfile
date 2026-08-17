# ---- Base image ----
FROM python:3.12-slim

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Working directory ----
WORKDIR /app

# ---- Dependencies (cached layer — changes rarely) ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Application code (changes often — comes after deps) ----
COPY ./app ./app
COPY alembic.ini .
COPY ./alembic ./alembic

# ---- Run as a non-root user ----
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# ---- Start the app ----
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
