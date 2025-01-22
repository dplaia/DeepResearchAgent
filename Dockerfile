# Use an official Python runtime as a parent image
FROM python

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Update package lists and upgrade apt-transport-https
RUN apt-get update
RUN apt-get install --reinstall -y apt-transport-https
RUN apt-get update

# Install Playwright with Chromium and dependencies for browser automation
RUN python -m playwright install --with-deps chromium

# Run crawl4ai setup and doctor commands
RUN crawl4ai-setup
RUN crawl4ai-doctor

# Copy the Python script into the container
COPY crawl_script.py .

# Command to run the Python script when the container starts
CMD ["python", "crawl_script.py"]
