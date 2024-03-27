# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed dependencies specified in requirements.txt
RUN apt-get update && apt-get install git -y
RUN pip3 install "git+https://github.com/openai/whisper.git"
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y ffmpeg


# Expose the port that FastAPI runs on
EXPOSE 8001

# Define environment variable for FastAPI to listen on all IPs
ENV HOST=0.0.0.0

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
