from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.store import Store
from app.models.product import Product
from app.models.member_level import MemberLevel, seed_member_levels
from app.models.admin import AdminUser, seed_admin_user


def seed_all_data(db: Session):
    """初始化所有基础数据"""
    seed_member_levels(db)
    seed_admin_user(db)
    seed_categories(db)
    seed_stores(db)
    seed_products(db)


def seed_categories(db: Session):
    """初始化分类数据"""
    if db.query(Category).first():
        return
    
    categories = [
        Category(name="自行车", icon="🚲", sort_order=1),
        Category(name="配件", icon="🔧", sort_order=2),
        Category(name="装备", icon="🪖", sort_order=3),
        Category(name="服饰", icon="👕", sort_order=4),
    ]
    for c in categories:
        db.add(c)
    db.commit()


def seed_stores(db: Session):
    """初始化门店数据"""
    if db.query(Store).first():
        return
    
    stores = [
        Store(
            name="AceOffix 旗舰店",
            province="北京市",
            city="北京",
            district="朝阳区",
            address="朝阳区建国路1号",
            phone="010-12345678",
            hours="09:00-21:00",
            status=1,
            sort_order=1,
            latitude=39.9042,
            longitude=116.4074
        ),
        Store(
            name="AceOffix 西湖店",
            province="浙江省",
            city="杭州",
            district="西湖区",
            address="西湖区文三路2号",
            phone="0571-87654321",
            hours="09:00-21:00",
            status=1,
            sort_order=2,
            latitude=30.2741,
            longitude=120.1551
        ),
    ]
    for s in stores:
        db.add(s)
    db.commit()


def seed_products(db: Session):
    """初始化商品数据"""
    if db.query(Product).first():
        return
    
    products = [
        Product(
            name="山地自行车 X1",
            subtitle="专业级山地车，铝合金车架",
            price=299900,
            original_price=399900,
            stock=50,
            category_id=1,
            images=["https://example.com/bike1.jpg"],
            specs=[{"key": "车架", "value": "铝合金"}, {"key": "变速", "value": "27速"}],
            status=1,
            sort_order=1
        ),
        Product(
            name="公路自行车 R2",
            subtitle="碳纤维公路车，轻量竞速",
            price=499900,
            original_price=599900,
            stock=30,
            category_id=1,
            images=["https://example.com/bike2.jpg"],
            specs=[{"key": "车架", "value": "碳纤维"}, {"key": "变速", "value": "22速"}],
            status=1,
            sort_order=2
        ),
        Product(
            name="自行车头盔",
            subtitle="轻量化安全头盔，通风透气",
            price=19900,
            original_price=29900,
            stock=200,
            category_id=3,
            images=["https://example.com/helmet.jpg"],
            specs=[{"key": "材质", "value": "EPS+PC"}, {"key": "重量", "value": "250g"}],
            status=1,
            sort_order=3
        ),
        Product(
            name="骑行手套",
            subtitle="半指手套，减震防滑",
            price=8900,
            original_price=12900,
            stock=300,
            category_id=2,
            images=["https://example.com/gloves.jpg"],
            specs=[{"key": "材质", "value": "莱卡+硅胶"}, {"key": "尺码", "value": "M/L/XL"}],
            status=1,
            sort_order=4
        ),
    ]
    for p in products:
        db.add(p)
    db.commit()
