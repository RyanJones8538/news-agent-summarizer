FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r /app/web/requirements.txt
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000"]