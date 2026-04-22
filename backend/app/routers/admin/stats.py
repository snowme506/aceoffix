from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.store import Store
from app.schemas.admin import StatsOverview
from app.schemas.common import ResponseModel
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/overview", response_model=ResponseModel[StatsOverview])
async def get_stats_overview(
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-统计概览"""
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_sales = db.query(func.coalesce(func.sum(Order.final_amount), 0)).scalar() or 0
    total_products = db.query(Product).count()
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = db.query(Order).filter(Order.created_at >= today_start).count()
    today_sales = db.query(func.coalesce(func.sum(Order.final_amount), 0)).filter(
        Order.created_at >= today_start
    ).scalar() or 0
    
    return ResponseModel(
        code=200,
        message="success",
        data=StatsOverview(
            total_users=total_users,
            total_orders=total_orders,
            total_sales=int(total_sales),
            total_products=total_products,
            today_orders=today_orders,
            today_sales=int(today_sales)
        )
    )


@router.get("/chart", response_model=ResponseModel[dict])
async def get_stats_chart(
    days: int = 7,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-订单/销售额趋势图"""
    if days < 1:
        days = 1
    elif days > 90:
        days = 90  # 最多查90天
    """后台-订单/销售额趋势图"""
    results = []
    for i in range(days - 1, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_orders = db.query(Order).filter(
            Order.created_at >= day_start,
            Order.created_at < day_end
        ).count()
        
        day_sales = db.query(func.coalesce(func.sum(Order.final_amount), 0)).filter(
            Order.created_at >= day_start,
            Order.created_at < day_end
        ).scalar() or 0
        
        results.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "orders": day_orders,
            "sales": int(day_sales)
        })
    
    return ResponseModel(code=200, message="success", data=results)
