FROM python:3.11-slim

WORKDIR /app

# Copy shared package into the image
COPY services/common/iamd_common ./iamd_common

COPY services/sensor-ingest/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/sensor-ingest/app ./app

# Make /app importable so `import iamd_common` works
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8001"]
