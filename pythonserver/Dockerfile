# Dockerfile that runs a sample Python Flask application with gunicorn on port 8080
FROM python:3.11.6-slim
EXPOSE 8080
RUN pip install flask gunicorn

WORKDIR /

# Copy the source code into the image for running
COPY . .

# Assuming we are running pinned on a single core, number of worker threads is set to 2 x <num cores> + 1 = 3 in our case
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "main:app"]
