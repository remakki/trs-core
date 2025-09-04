FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync

COPY . .

CMD ["uv", "run", "python", "-m", "src.main"]
