from fastapi import APIRouter, HTTPException, Depends

from ..services.firewall_service import FirewallService

router = APIRouter()


class FirewallStatusAPI:
    """
    Relay information about the status of the firewall
    """

    @staticmethod
    @router.get("/status")
    async def get_firewall_status(firewall_service: FirewallService = Depends()):
        try:
            return {"status": firewall_service.get_firewall_status()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def router() -> APIRouter:
        return router
