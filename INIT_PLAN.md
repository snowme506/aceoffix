# aceoffix 项目初始化方案

> 由 Kimi Agent 生成 | 2026-04-19

---

## 一、数据库表 SQL

```sql
-- ============================================================
-- aceoffix 微信服务系统 - 数据库初始化脚本
-- MySQL 8.0
-- ============================================================

CREATE DATABASE IF NOT EXISTS aceoffix DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aceoffix;

-- 1. 会员等级表
CREATE TABLE member_levels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL COMMENT '等级名（普通/银卡/金卡）',
    discount_rate DECIMAL(3,2) NOT NULL DEFAULT 1.00 COMMENT '折扣率（0.90=9折）',
    points_multiplier DECIMAL(2,1) NOT NULL DEFAULT 1.0 COMMENT '积分倍率',
    min_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '升级门槛（累计消费）',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='会员等级表';

-- 2. 用户表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像URL',
    level_id INT DEFAULT 1 COMMENT '会员等级',
    total_points INT DEFAULT 0 COMMENT '当前积分',
    total_spent DECIMAL(10,2) DEFAULT 0.00 COMMENT '累计消费金额',
    status TINYINT DEFAULT 1 COMMENT '1=正常 0=禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (level_id) REFERENCES member_levels(id)
) ENGINE=InnoDB COMMENT='用户表';

-- 3. 门店表
CREATE TABLE stores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '门店名称',
    province VARCHAR(20) COMMENT '省份',
    city VARCHAR(20) COMMENT '城市',
    district VARCHAR(20) COMMENT '区县',
    address VARCHAR(255) COMMENT '详细地址',
    lat DECIMAL(10,7) COMMENT '纬度',
    lng DECIMAL(10,7) COMMENT '经度',
    phone VARCHAR(20) COMMENT '门店电话',
    hours VARCHAR(100) COMMENT '营业时间',
    status TINYINT DEFAULT 1 COMMENT '1=营业 0=休息',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='门店表';

-- 4. 分类表
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL COMMENT '分类名',
    icon VARCHAR(255) COMMENT '图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status TINYINT DEFAULT 1 COMMENT '1=启用 0=禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='商品分类表';

-- 5. 商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL COMMENT '分类',
    store_id INT COMMENT '归属门店（NULL=全部门店）',
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    subtitle VARCHAR(200) COMMENT '副标题',
    price DECIMAL(10,2) NOT NULL COMMENT '售价',
    original_price DECIMAL(10,2) COMMENT '原价',
    stock INT DEFAULT 0 COMMENT '库存',
    images JSON COMMENT '图片列表 [url1, url2]',
    specs JSON COMMENT '规格选项 [{name:"颜色",values:["红","蓝"]}]',
    description TEXT COMMENT '详情描述',
    status TINYINT DEFAULT 1 COMMENT '1=上架 0=下架',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='商品表';

-- 6. 订单表
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL COMMENT '订单号',
    user_id BIGINT NOT NULL COMMENT '用户',
    store_id INT COMMENT '门店',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总价',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠金额',
    points_offset INT DEFAULT 0 COMMENT '积分抵扣（金额）',
    final_amount DECIMAL(10,2) NOT NULL COMMENT '实付金额',
    points_earned INT DEFAULT 0 COMMENT '获得积分',
    status TINYINT DEFAULT 1 COMMENT '1=待支付 2=已支付 3=已完成 4=已取消 5=退款中 6=已退款',
    remark VARCHAR(255) COMMENT '用户备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME COMMENT '支付时间',
    completed_at DATETIME COMMENT '完成时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (store_id) REFERENCES stores(id)
) ENGINE=InnoDB COMMENT='订单表';

-- 7. 订单明细表
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL COMMENT '订单',
    product_id INT NOT NULL COMMENT '商品',
    product_name VARCHAR(100) NOT NULL COMMENT '商品名称（冗余）',
    price DECIMAL(10,2) NOT NULL COMMENT '单价（冗余）',
    quantity INT NOT NULL COMMENT '数量',
    specs JSON COMMENT '用户选择的规格',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB COMMENT='订单明细表';

-- 8. 积分记录表
CREATE TABLE user_points_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户',
    type TINYINT NOT NULL COMMENT '1=消费得积分 2=积分兑换 3=积分抵扣 4=积分调整',
    points INT NOT NULL COMMENT '积分变动（正/负）',
    balance INT NOT NULL COMMENT '变动后余额',
    order_id BIGINT COMMENT '关联订单（可为NULL）',
    remark VARCHAR(100) COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='积分记录表';

-- 9. 系统配置表
CREATE TABLE configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    `key` VARCHAR(50) UNIQUE NOT NULL COMMENT '配置键',
    value JSON NOT NULL COMMENT '配置值',
    description VARCHAR(100) COMMENT '说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='系统配置表';

-- 10. 管理员表（B端登录用）
CREATE TABLE admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    name VARCHAR(50) COMMENT '姓名',
    role VARCHAR(20) DEFAULT 'staff' COMMENT '角色：super/admin/staff',
    status TINYINT DEFAULT 1 COMMENT '1=启用 0=禁用',
    last_login_at DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='管理员表';

-- 初始化数据
INSERT INTO member_levels (id, name, discount_rate, points_multiplier, min_amount, sort_order) VALUES
(1, '普通会员', 1.00, 1.0, 0.00, 1),
(2, '银卡会员', 0.95, 1.2, 1000.00, 2),
(3, '金卡会员', 0.90, 1.5, 5000.00, 3);

INSERT INTO configs (`key`, value, description) VALUES
('points_per_yuan', '1', '每消费1元得积分'),
('points_to_yuan', '100', '多少积分抵1元'),
('points_expiry_months', '12', '积分有效期（月）'),
('min_points_to_use', '100', '最低可用积分'),
('max_points_offset_rate', '0.2', '积分最高抵扣比例');

-- 创建索引
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_level ON users(level_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_store ON products(store_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_points_log_user ON user_points_log(user_id);
CREATE INDEX idx_stores_status ON stores(status);
```

---

## 二、FastAPI 项目目录结构

```
aceoffix/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── routers/           # API 路由
│   │   ├── services/          # 业务逻辑层
│   │   ├── utils/             # 工具函数
│   │   └── dependencies/      # 依赖注入
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── admin/                     # React 管理后台 (B端)
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 公共组件
│   │   ├── services/         # API 请求
│   │   ├── utils/            # 工具函数
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── miniprogram/               # 微信小程序 (C端)
│   ├── pages/                 # 页面
│   ├── components/            # 组件
│   ├── utils/                 # 工具
│   ├── services/             # API 请求
│   ├── app.js
│   ├── app.json
│   └── app.wxss
│
├── docker-compose.yml         # 本地开发环境
└── README.md
```

---

## 三、requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pymysql==1.1.0
redis==5.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
python-dotenv==1.0.0
```

---

## 四、下一步待确认

1. ✅ 数据库表结构是否 OK？
2. ✅ FastAPI 目录结构是否符合预期？
3. ⏳ 是否需要先创建项目骨架代码？
4. ⏳ 阿里云 RDS MySQL 创建进度？
5. ⏳ 第一期开发从哪个模块开始？
