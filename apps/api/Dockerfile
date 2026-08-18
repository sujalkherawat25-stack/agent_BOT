FROM python:3.12-slim
WORKDIR /workspace
COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY apps/api /workspace/apps/api
COPY packages /workspace/packages
ENV PYTHONPATH=/workspace/packages:/workspace/apps/api
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
