from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base
from app.utils.seed import seed_all_data
from app.routers import auth, users, orders, points, public, stores, categories, products, admin


app = FastAPI(
    title="AceOffix API",
    description="AceOffix 会员积分系统 API",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        seed_all_data(db)
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown():
    pass

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://101.201.181.170"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix="/api/auth", tags=["认证"])
app.include_router(users, prefix="/api/users", tags=["用户"])
app.include_router(orders, prefix="/api/orders", tags=["订单"])
app.include_router(points, prefix="/api/points", tags=["积分"])
app.include_router(public, prefix="/api", tags=["公共"])
app.include_router(stores, prefix="/api/stores", tags=["门店"])
app.include_router(categories, prefix="/api/categories", tags=["分类"])
app.include_router(products, prefix="/api/products", tags=["商品"])
app.include_router(admin, prefix="/api/admin", tags=["后台管理"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "aceoffix-api"}
