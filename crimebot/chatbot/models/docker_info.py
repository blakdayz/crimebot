from pydantic import BaseModel


class DockerInfo(BaseModel):
    containers: dict
    images: dict
    networks: list
