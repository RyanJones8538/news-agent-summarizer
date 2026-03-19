FROM python:3.11-slim

WORKDIR /app

COPY web/ /app/web/
COPY common/ /app/common/

RUN pip install -r /app/web/requirements.txt
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]