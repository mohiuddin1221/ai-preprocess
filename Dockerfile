FROM python:3.10-slim


# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the required packages

COPY main.py .

CMD ["python", "main.py"]
