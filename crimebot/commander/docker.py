import docker
from docker_compose import Compose
from fastapi import FastAPI, HTTPException, status, Depends
from prometheus_client import Gauge

COMPOSE_FILE = "docker-compose.yml"
DOCKER_COMPOSE = Compose(COMPOSE_FILE)
DOCKER_CONTAINERS_GAUGE = Gauge("docker_containers_running", "Number of running Docker Compose containers")

def check_docker_daemon():
    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Docker daemon is not running: {e}",
        )

def start_containers(daemon_check: bool = Depends(check_docker_daemon)):
    DOCKER_COMPOSE.up(detached=True)
    DOCKER_CONTAINERS_GAUGE.set(len(get_running_containers()))

def get_running_containers():
    compose_file_path = find_docker_compose_file(COMPOSE_FILE)
    compose_data = load_compose_data(compose_file_path)
    container_names = {service["name"] for service in compose_data["services"].values()}

    client = docker.from_env()
    containers = client.containers.list(all=True)

    running_containers = {container.name for container in containers if container.status == "running"}

    return container_names & running_containers
