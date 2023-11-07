# Using 3 worker threads for a single core as recommended by https://docs.gunicorn.org/en/stable/design.html#how-many-workers
# No OpenTelemetry instrumentation enabled
taskset -c 0 gunicorn -w 3 -b 0.0.0.0:8080 main:app