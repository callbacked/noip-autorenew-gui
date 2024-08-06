# Use the official Docker-in-Docker image
FROM docker:23.0.1-dind

# Install necessary packages
RUN apk add --no-cache python3 py3-pip

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]
