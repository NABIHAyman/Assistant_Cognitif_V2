# mcp-server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Le protocole MCP utilise souvent les flux standard (stdio) ou HTTP/SSE (port 8000)
EXPOSE 8000

CMD ["python", "server.py"]