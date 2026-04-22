# app/routers/__init__.py
from app.routers.auth import router as auth
from app.routers.users import router as users
from app.routers.orders import router as orders
from app.routers.points import router as points
from app.routers.public import router as public
from app.routers.stores import router as stores
from app.routers.categories import router as categories
from app.routers.products import router as products
from app.routers.admin import router as admin

__all__ = ["auth", "users", "orders", "points", "public", "stores", "categories", "products", "admin"]
