# Start from your base image with Node and Python
FROM zenontum/my-shacl-app:latest

# Set the working directory for the container
WORKDIR /app

# Copy backend files and install dependencies
COPY ./backend ./backend
WORKDIR /app/backend
RUN pip3 install -r requirements.txt

# Copy frontend files and install dependencies
WORKDIR /app
COPY ./frontend ./frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# (Optional) If you need to serve the frontend build with the backend,
# copy the build artifacts to the backend's static directory
# RUN cp -r /app/frontend/build /app/backend/static/

# Set the working directory to backend to run the server
WORKDIR /app/backend

# Expose the necessary port
EXPOSE 80

# Specify the command to run the Python backend server
CMD ["python3", "app.py"]