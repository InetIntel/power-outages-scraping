# Aneel

## TLDR

```
# 0. Start the containers
make run

# 1. Build and publish the image to registry
make publish

# 2. Verify that image was published to the registry
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

Navigate to DAGU to run dags: `localhost:8080`

Block storage: `localhost:9090`

## Developer workflow

1. Create `scrape.py` and `post_process.py` scripts
2. Define the container image in a `Dockerfile`
3. Define the DAG in **dagu_config/dags**
4. Publish to image registry `make publish`

## Architecture

![Architecture](./docs/img/Architecture.jpg)

## Architecture TBD

![Architecture Ideal](./docs/img/Architecture-Ideal.jpg)

## Resources

<https://github.com/dagu-org/dagu>

<https://github.com/minio/minio>
