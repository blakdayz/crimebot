from fastapi import APIRouter, HTTPException

from ..models.project_config import ProjectConfig
from ..services.project_service import ProjectService

router = APIRouter()


class CreatePythonProjectAPI:
    """
    Generates python projects based on cookie cutter project configs
    """

    @router.post("/create")
    async def create_python_project(project_config: ProjectConfig):
        try:
            project_service = ProjectService()
            project_path = project_service.create_project(**project_config.dict())
            return {"project_path": project_path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def router() -> APIRouter:
        return router
