import asyncio

from fastapi import APIRouter, HTTPException

from crimebot.chatbot.models import NmapScanIn
from crimebot.chatbot.services import NMAPService

router = APIRouter()


class NMAPScanAPI:
    """
    Provide NMAP scanning capability to the bot
    """

    @staticmethod
    @router.post("/scan")
    async def scan_hosts(nmap_target: str):
        try:
            nmap_service = NMAPService()
            results = await nmap_service.scan_hosts(nmap_target)
            return [NmapScanIn(**result) for result in results]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def router() -> APIRouter:
        return router


if __name__ == "__main__":
    api = NMAPScanAPI()
    asyncio.run(api.scan_hosts("192.168.86.1"))
