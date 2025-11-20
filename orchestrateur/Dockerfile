FROM ubuntu:22.04

# Set non-interactive frontend for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists, upgrade packages, install git, and clean up
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository
RUN git clone https://github.com/firasbouzazi/projet_commande

# Set the working directory to the cloned project
WORKDIR /app/projet_commande

# Make the setup script executable and run it
RUN chmod +x ./setup.sh && \
    ./setup.sh
