FROM ubuntu:22.04

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Git LFS
RUN apt-get update && apt-get install -y git-lfs && rm -rf /var/lib/apt/lists/*
RUN git lfs install

# Clone the dataset with Git LFS
RUN git clone https://huggingface.co/datasets/AyoubChLin/CompanyDocuments /data/CompanyDocuments

# Install Python dependencies
RUN pip3 install --no-cache-dir psycopg2-binary datasets requests

# Copy the script
COPY download_BDD.py .

# Wait for postgres, then run the script
CMD ["python3", "download_BDD.py"]
