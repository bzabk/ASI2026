FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY tests/ ./tests/
CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000"]
