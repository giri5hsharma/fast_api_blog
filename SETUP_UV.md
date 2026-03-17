# Setup with uv

This project uses dependencies defined in `pyproject.toml`, so `uv` can create and manage the environment directly.

## 1. Install uv

If you do not already have uv installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
```

## 2. Go to the project folder

```bash
cd /Users/girishsharma/Desktop/fastapi_blog
```

## 3. Create environment and install dependencies

```bash
uv sync
```

This will:

- create a virtual environment (if missing)
- install all dependencies from `pyproject.toml`

## 4. Run the app

Use either FastAPI CLI or Uvicorn.

FastAPI CLI:

```bash
uv run fastapi dev main.py
```

Uvicorn:

```bash
uv run uvicorn main:app --reload
```

## 5. Open API docs

After server starts:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Useful uv commands

Install one extra package:

```bash
uv add <package-name>
```

Re-sync dependencies after updates:

```bash
uv sync
```

Run any Python command inside project environment:

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```
