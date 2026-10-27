FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY diffgate /app/diffgate

ENTRYPOINT ["python", "-m", "diffgate.cli", "--ci", "--post-to-pr"]
