import os
import asyncio
import subprocess
from typing import Dict, Any

import uvicorn
import yaml
from fastapi import FastAPI, Depends, HTTPException
import requests

from docker.client import DockerClient
from docker.errors import ContainerError

app = FastAPI()

DOCKER_COMPOSE_FILE = "cconf/docker-compose.yaml"

# Use environment variables for Docker socket and image name
DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
IMAGE_NAME = os.getenv("IMAGE_NAME", "your_image_name")

DOCKER_CLIENT = DockerClient(base_url=f"unix://{DOCKER_SOCKET}")


def get_docker_compose() -> Dict[str, Any]:
    with open(DOCKER_COMPOSE_FILE) as f:
        return yaml.safe_load(f)


async def start():
    docker_compose = get_docker_compose()
    container_name = next(iter(docker_compose["services"]))

    try:
        existing_container = DOCKER_CLIENT.containers.get(container_name)
    except ContainerError:
        # Container does not exist, create a new one
        service_config = docker_compose["services"][container_name]
        command = [service_config["deploy"]["run"]["command"]] + service_config["deploy"]["run"]["args"]
        existing_container = DOCKER_CLIENT.containers.run(
            image=IMAGE_NAME,
            name=container_name,
            detach=True,
            command=command
        )
    else:
        if existing_container.status != "running":
            raise HTTPException(status_code=500, detail="Container is not running.")

    # Install Metasploit in the container once it's running
    await asyncio.sleep(60)  # Wait for 1 minute to allow the container to start fully

    install_msf_command = (
        f"docker exec -it {existing_container.id} /bin/sh -c 'apk add --no-cache git && "
        f"cd /app && git clone https://github.com/rapid7/metasploit-framework.git /opt/metasploit-framework && "
        f"cd /opt/metasploit-framework && ./msfupdate'"
    )
    subprocess.run(install_msf_command, shell=True, check=True)

    return {"message": "Docker container started and Metasploit installed."}


@app.post("/start")
async def start_endpoint():
    return await start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
