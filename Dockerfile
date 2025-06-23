FROM python:3.13

# Set the working directory in the container
WORKDIR /app

RUN pip install --upgrade pip

# Copy only the required files into the container
COPY requirements.txt ./

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

RUN chown -R 1001:0 /app
# Adjust permissions on workdir so writable by group root.
RUN chmod -R g+w /app

USER 1001

# Define environment variable for Python to avoid buffering
ENV PYTHONUNBUFFERED=1
ENV PORT 8080
EXPOSE 8080

CMD ["gunicorn","--config", "gunicorn_config.py", "server:app"]
