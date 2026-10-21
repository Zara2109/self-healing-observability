
FROM python:3.12-slim

RUN pip install --no-cache-dir ansible-core docker Flask==3.1.2
RUN ansible-galaxy collection install community.docker

WORKDIR /workspace

CMD ["python", "/workspace/recovery_api.py"]
