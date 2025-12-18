FROM python:3.11-slim

WORKDIR /app

# shared library
COPY services/common/iamd_common ./iamd_common

COPY services/track-fusion/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/track-fusion/app ./app

ENV PYTHONPATH=/app

EXPOSE 8002
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8002"]
