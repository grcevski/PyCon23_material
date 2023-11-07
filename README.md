# PyCon2023 Ireland Material and Experiments
Beyla PyCon 2023 Ireland Material

## Introduction

We performed a set of measurements with three separate configurations:

1. A simple un-instrumented Python Flask application running on a single core
   with 3 `gunicorn` sync workers. The API we are using is purely CPU bound and
   sync workers was the optimal configuration.
2. The same Python Flask application as in 1., instrumented with the Python Flask
   [OpenTelemetry Automatic Instrumentation](https://opentelemetry.io/docs/instrumentation/python/automatic/).
3. The same Python Flask application as in 2., instrumented at system level with eBPF
   by using [Beyla](https://github.com/grafana/beyla).

The measurement of latencies was performed by running an HTTP driver script, pushing
constant QPS, which was varied from 250 QPS to 1250 QPS. The load generation was done
with [wrk2](https://github.com/giltene/wrk2) which has very minimal CPU overhead. 

## Methodology

Since we are interested in stable measurement of tail latencies, we ran the Python application
and Beyla on bare metal hardware, while we kept all of the trace databases and OpenTelemetry 
collector components running inside Docker, pinned on other CPU cores. This ensures minimal
interference and simulates what would happen in a properly provisioned Kubernetes environment.

Similarly we pinned the Python application to a single core, so that we can run the experiments
properly, simulating a more realistic scenario for a Python micro-service in a Kubernetes
environment. Running with higher QPS, for example 10,000 QPS on a 16-core machine would also be
possible, but we'd need to have a much more capable trace database infrastructure, so that it can
scale with the amount of data we are producing. Scaling such infrastructure is beyond the scope
of this presentation, so we focused on a single micro-service scenario.

## How to run the experiments

Grafana provides a packaged Docker image of the [OpenSource LGTM](https://github.com/grafana/docker-otel-lgtm) 
stack including the OpenTelemetry Collector. We used this Github repository to have a functioning 
Trace database (Tempo) with a Grafana instance, so that we can check if we are correctly producing the data, 
and to validate the number of events between the setup scenarios.

Once you've downloaded the LGTM stack repo, run the following commands:

```sh
cd docker
docker build . -t grafana/otel-lgtm
taskset -c 1-16 docker run -p 3000:3000 -p 4317:4317 --rm -ti grafana/otel-lgtm
```

The `taskset` command above is assuming that we 16 cores and you may want to adjust that to the number of 
cores you have available on your system. We skip the first core (core 0) to make sure we don't interfere
with the Python application which we'll pin to core 0. If you have hyperthreading enabled on your system
you may want to skip both core 0 and 1, in case your cores are enumerated as physical then virtual.

Next, to run the application check the `run.sh` scripts in the `pythonserver` and the `pythonserver-otel`
directories. You'll notice that we pin the `gunicorn` processes to core 0. For example:

```sh
taskset -c 0 gunicorn -w 3 -b 0.0.0.0:8080 main:app
```

Finally, we can generate some load. For that we'll use the `work.sh` script, which assumes you have `wrk2`
installed on your system:

```sh
taskset -c 1-16 ./work.sh 250
```

In the example above we also prevent wrk2 from running on core 0 and we run the load generator with
250 QPS.

## Measurements

We collected a set of measurements on 12th Gen Intel(R) Core(TM) i7-1280P 2 GHz (Linux version 6.2.0-36-generic),
running each scenario 3 times to make sure we can either take average latencies or best of 3.

The results can be found in the file measurements.txt.

Notice that we didn't run the OpenTelemetry Auto Instrumentation scenario with 1250 QPS, because we were
already out of CPU resources at 1000 QPS. Running beyond 1000 QPS would not be sustainable and the application
would create a backlog and not be able to achieve the desired QPS. Essentially, we'd get response times
in seconds instead of the usual millisecond range.