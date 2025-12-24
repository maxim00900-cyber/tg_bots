from aiogram import Router

from .crypto import router as crypto_router
from .rub import router as rub_router
from .admin import router as admin_router
from .common import router as main_router

router = Router()
router.include_router(crypto_router)
router.include_router(rub_router)
router.include_router(admin_router)
router.include_router(main_router)
