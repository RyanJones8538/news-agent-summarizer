FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r /app/retrieval/requirements.txt
CMD ["uvicorn", "retrieval.retrieval:app", "--host", "0.0.0.0", "--port", "8000"]