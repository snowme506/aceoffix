from fastapi import APIRouter

from app.routers.admin.auth import router as auth_router
from app.routers.admin.stores import router as stores_router
from app.routers.admin.categories import router as categories_router
from app.routers.admin.products import router as products_router
from app.routers.admin.members import router as members_router
from app.routers.admin.orders import router as orders_router
from app.routers.admin.stats import router as stats_router
from app.routers.admin.upload import router as upload_router
from app.routers.admin.banners import router as banners_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["后台-认证"])
router.include_router(stores_router, prefix="/stores", tags=["后台-门店"])
router.include_router(categories_router, prefix="/categories", tags=["后台-分类"])
router.include_router(products_router, prefix="/products", tags=["后台-商品"])
router.include_router(members_router, prefix="/members", tags=["后台-会员"])
router.include_router(orders_router, prefix="/orders", tags=["后台-订单"])
router.include_router(stats_router, prefix="/stats", tags=["后台-统计"])
router.include_router(upload_router, prefix="/upload", tags=["后台-上传"])
router.include_router(banners_router, prefix="/banners", tags=["后台-轮播图"])
