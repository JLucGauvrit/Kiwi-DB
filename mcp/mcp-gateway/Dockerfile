FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   libpq-dev \
	   libffi-dev \
	   libssl-dev \
	   ca-certificates \
	   rustc \
	   cargo \
	&& python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get purge -y --auto-remove build-essential gcc \
	&& rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 9000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
