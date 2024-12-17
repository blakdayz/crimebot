import yaml
from fastapi import FastAPI, Depends, HTTPException
import subprocess
import os
import requests
from dotenv import load_dotenv
from docker.client import DockerClient

load_dotenv()
DOCKER_COMPOSE_FILE = ".conf/docker-compose.yaml"
DOCKER_COMPOSE_COMMAND = "docker-compose up --build -d"
DOCKER_CLIENT = DockerClient(base_url="unix://" + os.environ["DOCKER_SOCKET"])


def get_docker_compose():
    with open(DOCKER_COMPOSE_FILE) as f:
        return yaml.safe_load(f)


app = FastAPI()


@app.post("/start")
async def start():
    docker_compose = get_docker_compose()
    container_name = docker_compose["services"][0]["name"]
    existing_container = DOCKER_CLIENT.containers.get(container_name)

    if existing_container:
        if not existing_container.status == "running":
            raise HTTPException(status_code=500, detail="Container is not running.")
    else:
        docker_compose_run = docker_compose["services"][0]["deploy"]["run"]
        command = [docker_compose_run["command"]]
        for arg in docker_compose_run["args"]:
            command.append(arg)

        container = DOCKER_CLIENT.create_container(
            image="your_image_name", name=container_name, command=command
        )
        container.start()

    # Install Metasploit in the container once it's running
    container_logs = DOCKER_CLIENT.logs(container, stdout=True, stderr=True)
    container_id = container.id
    for line in container_logs:
        if "Starting" in line and container_name in line:
            break

    # Wait until the container is up before running additional commands
    DOCKER_WAIT_TIMEOUT = 60
    timeout = time.time() + DOCKER_WAIT_TIMEOUT
    while True:
        container_status = DOCKER_CLIENT.inspect_container(container_id)["State"][
            "Status"
        ]
        if container_status == "running":
            break
        if time.time() > timeout:
            raise HTTPException(
                status_code=500,
                detail="Container did not start within the specified timeout.",
            )
        time.sleep(1)

    # Run the command to install Metasploit in the container
    install_msf_command = "docker exec -it {} /bin/sh -c 'apk add --no-cache git && cd /app && git clone https://github.com/rapid7/metasploit-framework.git /opt/metasploit-framework && cd /opt/metasploit-framework && ./msfupdate'"
    subprocess.run(install_msf_command.format(container_id), shell=True, check=True)

    return {"message": "Docker container started and Metasploit installed."}
