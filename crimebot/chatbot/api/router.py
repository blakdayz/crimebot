from fastapi import APIRouter


router = APIRouter()

router.include_router(router=router, prefix="/docker", tags=["Docker"])
router.include_router(router=router, prefix="/firewall", tags=["Firewall"])
router.include_router(router=router, prefix="/nmap", tags=["NMAP"])
router.include_router(router=router, prefix="/project", tags=["Project"])
