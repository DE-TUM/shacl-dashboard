# Start from your base image with Node+Python
FROM zenontum/my-shacl-env:v1.0.0

# Set a working directory
WORKDIR /app

# Copy your code into the container
COPY . .

# (Optional) Build the Vue frontend
# - If you want to serve a production build, do:
RUN npm install && npm run build

# For Python, if your base already installed requirements, we may skip.
# But if you have a separate requirements.txt or changed dependencies, do:
RUN pip3 install -r ./src/service/requirements.txt

# Example: If you want to run the Python server only:
CMD [ "python3", "src/service/app.py" ]
