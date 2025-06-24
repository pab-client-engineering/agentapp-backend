FROM registry.access.redhat.com/ubi9/python-312:latest

# Set the working directory in the container
USER 0
RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip

# Copy only the required files into the container
COPY requirements.txt ./

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

# Make dirs for files
RUN mkdir /app/pliki

RUN chown -R 1001:0 /app
# Adjust permissions on workdir so writable by group root.
RUN chmod -R g+w /app

USER 1001

# Define environment variable for Python to avoid buffering
ENV PYTHONUNBUFFERED=1
ENV PORT 8080
EXPOSE 8080

CMD ["gunicorn","--config", "gunicorn_config.py", "server:app"]
