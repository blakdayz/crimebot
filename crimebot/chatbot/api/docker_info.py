from fastapi import APIRouter, HTTPException, Depends

from crimebot.chatbot.services import DockerService, get_docker_info

router = APIRouter()


class DockerInfoAPI:
    """
    Get information about the Docker subsystem
    """

    @staticmethod
    @router.get("/info")
    async def get_docker_info(docker_service: DockerService = Depends(get_docker_info)):
        try:
            return docker_service.get_docker_info()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def router() -> APIRouter:
        return router


class DockerExecutionAPI:
    """
    Execute a command against a docker instance
    """

    @staticmethod
    @router.post("/exec")
    async def execute_command(
        command: str, docker_service: DockerService = Depends(get_docker_info)
    ):
        """
        Executes a docker command against a given
        :param command: The shell command to execute
        :param docker_service: An instance of the docker_service to us
        :return:
        """
        try:
            return docker_service.execute_command(command)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def router(self) -> APIRouter:
        return router
