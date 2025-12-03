FROM ubuntu:22.04

# Set non-interactive frontend for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists, upgrade packages, install git, python3 and pip, and clean up
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository
RUN git clone https://github.com/firasbouzazi/projet_commande

# Set the working directory to the cloned project
WORKDIR /app/projet_commande

# Copy requirements.txt and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY main.py ./main.py

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
