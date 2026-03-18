FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r /app/analysis/requirements.txt
CMD ["uvicorn", "analysis.analysis:app", "--host", "0.0.0.0", "--port", "8000"]