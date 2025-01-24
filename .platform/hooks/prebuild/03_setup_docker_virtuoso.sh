#!/bin/bash
# echo "Setting up Docker and running Virtuoso in a container..."

# # Install Docker
# echo "Installing Docker..."
# sudo dnf -y install docker
# if [ $? -ne 0 ]; then
#     echo "Failed to install Docker. Exiting."
#     exit 1
# fi

# sudo systemctl enable docker
# sudo systemctl start docker

# # Check if Docker started successfully
# if ! systemctl is-active --quiet docker; then
#     echo "Docker service failed to start. Exiting."
#     exit 1
# fi

# # Pull and run Virtuoso Docker image
# echo "Pulling Virtuoso Docker image..."
# if ! docker pull tenforce/virtuoso; then
#     echo "Failed to pull Virtuoso Docker image. Check if the image exists or requires authentication."
#     exit 1
# fi

# echo "Running Virtuoso Docker container..."
# if ! docker run -d --name virtuoso \
#     -p 8890:8890 -p 1111:1111 \
#     tenforce/virtuoso; then
#     echo "Failed to run Virtuoso Docker container. Exiting."
#     exit 1
# fi

# # Verify Docker container is running
# if [ "$(docker ps -q -f name=virtuoso)" ]; then
#     echo "Virtuoso Docker container is running."
# else
#     echo "Failed to start Virtuoso Docker container."
#     exit 1
# fi

# echo "Virtuoso setup complete. Accessible at http://localhost:8890"
