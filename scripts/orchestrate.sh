#!/usr/bin/env bash
# Orchestrate full MVP setup and start periodic verification (every 10 minutes)

PROJECT_ROOT="/Users/lluengo/Documents/dev/vinculia"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
LOG_DIR="$PROJECT_ROOT/logs"

mkdir -p "$LOG_DIR"

# ---- Install dependencies ----
echo "Installing backend dependencies..."
cd "$BACKEND_DIR"
if [ -f requirements.txt ]; then
  pip install -r requirements.txt > "$LOG_DIR/backend_install.log" 2>&1
fi

echo "Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ -f package.json ]; then
  npm install > "$LOG_DIR/frontend_install.log" 2>&1
fi

# ---- Run database migrations ----
cd "$BACKEND_DIR"
if command -v alembic >/dev/null 2>&1; then
  alembic upgrade head > "$LOG_DIR/alembic.log" 2>&1
else
  echo "Alembic not found; skipping migration" > "$LOG_DIR/alembic.log"
fi

# ---- Start servers (background) ----
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

echo "Backend PID $BACKEND_PID" > "$LOG_DIR/backend.pid"

cd "$FRONTEND_DIR"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo "Frontend PID $FRONTEND_PID" > "$LOG_DIR/frontend.pid"

# ---- Periodic health checks every 10 minutes ----
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; do
  echo "Running health checks at $(date)" >> "$LOG_DIR/orchestrator.log"
  $SCRIPTS_DIR/check_backend.sh >> "$LOG_DIR/orchestrator.log" 2>&1
  $SCRIPTS_DIR/check_frontend.sh >> "$LOG_DIR/orchestrator.log" 2>&1
  sleep 600
done

echo "One of the servers has stopped. Exiting orchestrator." >> "$LOG_DIR/orchestrator.log"
