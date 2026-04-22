# aceoffix 微信服务系统 — 技术规格文档

> 版本: v1.0
> 日期: 2026-04-19
> 状态: 初稿，待确认

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      微信小程序 (C端)                     │
│  会员注册 | 产品展示 | 积分查询 | 购买记录 | 门店查询 | 客服  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS API
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI 后端 (Python)                  │
│  用户服务 | 积分服务 | 订单服务 | 商品服务 | 门店服务 | 客服服务 │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐    ┌───────────┐   ┌───────────┐
   │  MySQL   │    │   Redis   │   │  微信 API  │
   │ (主数据) │    │ (缓存/会话) │   │ (登录/推送) │
   └──────────┘    └───────────┘   └───────────┘
                                                 
┌──────────────────────────────────────────────────────────┐
│                   Web管理后台 (B端)                       │
│  门店管理 | 商品管理 | 会员管理 | 订单管理 | 积分管理 | 统计   │
└──────────────────────────────────────────────────────────┘
```

---

## 二、品牌与产品信息

| 项目 | 内容 |
|------|------|
| 品牌名称 | aceoffix |
| 产品类型 | 自行车及配件 |
| 多门店 | 是（多门店管理系统） |

---

## 三、数据库设计

### 3.1 ER总图

```
users ─────< orders ─────< order_items
  │              │
  │              └────── products
  │
  ├────< user_points_log
  │
  └────< user_coupons

stores ─────< products
  │
  └────< staff

categories
  │
  └────< products

configs (KV配置表)
```

### 3.2 核心表结构

#### 用户表 `users`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| phone | VARCHAR(20) UNIQUE | 手机号 |
| nickname | VARCHAR(50) | 昵称 |
| avatar | VARCHAR(255) | 头像URL |
| level_id | INT FK | 会员等级 |
| total_points | INT | 当前积分 |
| created_at | DATETIME | 注册时间 |
| updated_at | DATETIME | 更新时间 |

#### 会员等级表 `member_levels`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| name | VARCHAR(20) | 等级名（普通/银卡/金卡） |
| discount_rate | DECIMAL(3,2) | 折扣率（0.90 = 9折） |
| points_multiplier | DECIMAL(2,1) | 积分倍率 |
| min_amount | DECIMAL(10,2) | 升级门槛（累计消费） |
| sort_order | INT | 排序 |

#### 门店表 `stores`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| name | VARCHAR(50) | 门店名称 |
| province | VARCHAR(20) | 省份 |
| city | VARCHAR(20) | 城市 |
| district | VARCHAR(20) | 区县 |
| address | VARCHAR(255) | 详细地址 |
| lat | DECIMAL(10,7) | 纬度 |
| lng | DECIMAL(10,7) | 经度 |
| phone | VARCHAR(20) | 门店电话 |
| hours | VARCHAR(100) | 营业时间 |
| status | TINYINT | 1=营业 0=休息 |
| sort_order | INT | 排序 |

#### 分类表 `categories`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| name | VARCHAR(30) | 分类名 |
| icon | VARCHAR(255) | 图标URL |
| sort_order | INT | 排序 |

#### 商品表 `products`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| category_id | INT FK | 分类 |
| store_id | INT FK | 归属门店（NULL=全部门店） |
| name | VARCHAR(100) | 商品名称 |
| subtitle | VARCHAR(200) | 副标题 |
| price | DECIMAL(10,2) | 售价 |
| original_price | DECIMAL(10,2) | 原价 |
| stock | INT | 库存 |
| images | JSON | 图片列表 [url1, url2] |
| specs | JSON | 规格选项 [{name:"颜色",values:["红","蓝"]}] |
| description | TEXT | 详情描述 |
| status | TINYINT | 1=上架 0=下架 |
| created_at | DATETIME | 创建时间 |

#### 订单表 `orders`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| order_no | VARCHAR(32) UNIQUE | 订单号 |
| user_id | BIGINT FK | 用户 |
| store_id | INT FK | 门店 |
| total_amount | DECIMAL(10,2) | 订单总价 |
| discount_amount | DECIMAL(10,2) | 优惠金额 |
| points_offset | INT | 积分抵扣（金额） |
| final_amount | DECIMAL(10,2) | 实付金额 |
| points_earned | INT | 获得积分 |
| status | TINYINT | 订单状态 |
| remark | VARCHAR(255) | 用户备注 |
| created_at | DATETIME | 下单时间 |
| paid_at | DATETIME | 支付时间 |

**订单状态**:
- 1 = 待支付
- 2 = 已支付/制作中
- 3 = 已完成
- 4 = 已取消
- 5 = 退款中
- 6 = 已退款

#### 订单明细表 `order_items`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| order_id | BIGINT FK | 订单 |
| product_id | INT FK | 商品 |
| product_name | VARCHAR(100) | 商品名称（冗余） |
| price | DECIMAL(10,2) | 单价（冗余） |
| quantity | INT | 数量 |
| specs | JSON | 用户选择的规格 |

#### 积分记录表 `user_points_log`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| user_id | BIGINT FK | 用户 |
| type | TINYINT | 变动类型 |
| points | INT | 积分变动（正/负） |
| balance | INT | 变动后余额 |
| order_id | BIGINT FK | 关联订单（可为NULL） |
| remark | VARCHAR(100) | 备注 |
| created_at | DATETIME | 时间 |

**积分变动类型**:
- 1 = 消费得积分
- 2 = 积分兑换
- 3 = 积分抵扣
- 4 = 积分调整（后台手动）

#### 系统配置表 `configs`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| key | VARCHAR(50) UNIQUE | 配置键 |
| value | JSON | 配置值 |
| description | VARCHAR(100) | 说明 |

**可配置项**:
| key | 说明 | 示例 |
|-----|------|------|
| points_per_yuan | 每消费1元得积分 | 1 |
| points_to_yuan | 多少积分抵1元 | 100 |
| points_expiry_months | 积分有效期（月） | 12 |
| min_points_to_use | 最低可用积分 | 100 |
| max_points_offset_rate | 积分最高抵扣比例 | 0.2 |

---

## 四、API接口设计

### 4.1 用户模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/phone/send-code` | 发送手机验证码 |
| POST | `/api/v1/auth/phone/login` | 手机号+验证码登录 |
| GET | `/api/v1/users/me` | 获取当前用户信息 |
| PUT | `/api/v1/users/me` | 更新个人信息 |
| GET | `/api/v1/users/me/points` | 获取积分详情+明细 |

### 4.2 商品模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/categories` | 获取商品分类 |
| GET | `/api/v1/products` | 商品列表（支持分类/搜索/门店筛选） |
| GET | `/api/v1/products/{id}` | 商品详情 |

### 4.3 门店模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/stores` | 门店列表 |
| GET | `/api/v1/stores/nearby` | 附近门店（LBS，按距离排序） |
| GET | `/api/v1/stores/{id}` | 门店详情 |

### 4.4 订单模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/orders` | 创建订单 |
| GET | `/api/v1/orders` | 订单列表（分页+状态筛选） |
| GET | `/api/v1/orders/{id}` | 订单详情 |
| PUT | `/api/v1/orders/{id}/cancel` | 取消订单（未支付） |
| POST | `/api/v1/orders/{id}/pay` | 模拟支付 |

### 4.5 积分模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/points/rules` | 积分规则说明 |
| GET | `/api/v1/points/exchange-products` | 可用积分兑换的商品列表 |
| POST | `/api/v1/points/exchange` | 积分兑换 |

### 4.6 管理后台 API

| 方法 | 路径 | 说明 |
|------|------|------|
| — | `/api/v1/admin/stores/*` | 门店管理（CRUD） |
| — | `/api/v1/admin/products/*` | 商品管理（CRUD+上下架） |
| — | `/api/v1/admin/categories/*` | 分类管理（CRUD） |
| — | `/api/v1/admin/members/*` | 会员列表/搜索/详情/积分调整 |
| — | `/api/v1/admin/orders/*` | 订单列表/状态管理/导出 |
| — | `/api/v1/admin/points/*` | 积分规则配置 |
| — | `/api/v1/admin/levels/*` | 会员等级配置 |
| — | `/api/v1/admin/configs/*` | 系统配置管理 |
| — | `/api/v1/admin/stats/*` | 数据统计（日报/月报） |

---

## 五、C端小程序页面

```
pages/
├── index          首页（轮播+分类入口+热卖商品）
├── category       分类页（分类列表+商品筛选）
├── product        商品详情（规格选择+加入订单）
├── store          门店列表（附近/全部）
├── store-detail   门店详情（信息+导航按钮）
├── order          订单确认页（门店+商品+积分抵扣）
├── order-list     订单列表（全部/待支付/已完成）
├── order-detail   订单详情（状态+操作按钮）
├── points         积分中心（余额+规则+兑换入口）
├── points-log     积分明细（收入/支出记录）
├── profile        个人中心（信息+等级+设置）
└── login          手机号登录
```

---

## 六、B端管理后台页面

```
Admin/
├── /login                管理员登录
├── /dashboard            数据概览（今日订单/额/新会员）
├── /stores               门店管理（增删改+开关店）
├── /products             商品管理（分类+列表+上下架）
├── /members              会员管理（列表+详情+积分调整）
├── /orders               订单管理（全部/待处理/已完成/退款）
├── /points               积分规则配置
├── /levels               会员等级配置
├── /stats                数据统计（销售/会员/积分报表）
└── /settings             系统配置
```

---

## 七、分期开发计划

### 第一期（Mock系统）— 预计 4~5 周

| 周次 | 模块 | 主要内容 |
|------|------|---------|
| 第1周 | 基础设施 | 数据库搭建 + FastAPI框架 + 管理后台骨架 + 管理员登录 |
| 第2周 | 用户+积分 | 手机号登录 + 会员管理 + 积分系统（规则可配置） |
| 第3周 | 商品+门店 | 商品CRUD + 分类管理 + 门店管理 + 附近门店LBS |
| 第4周 | 订单+小程序 | 订单流程 + Mock支付 + 小程序前端主要页面 |
| 第5周 | 收尾 | 管理后台完善 + 积分兑换 + 客服入口 |

### 第二期（微信集成，后续接入）

- 微信一键登录
- 微信模板消息推送
- 微信支付（可选）

---

## 八、技术栈汇总

| 项目 | 技术选型 |
|------|---------|
| 后端框架 | Python 3.11 + FastAPI |
| 数据库 | MySQL 8.0（阿里云RDS） |
| 缓存 | Redis |
| 小程序 | 微信小程序原生 |
| B端前端 | React + Ant Design Pro |
| 部署 | Docker + 阿里云ECS |
| 微信集成 | 公众号授权 + 客服消息 + 模板消息（第二期） |

---

## 九、项目仓库

待创建，建议仓库名：`aceoffix`

---

## 十、确认事项

在开发启动前需确认：
1. ✅ 技术方案是否OK
2. ✅ 数据库表结构是否有遗漏
3. ✅ API接口是否满足业务需求
4. ✅ 页面清单是否完整
5. ✅ 分期计划工期是否可接受
6. ⏳ 微信服务号 AppID/Secret（第二期前提供即可）
7. ⏳ 阿里云RDS MySQL 创建（第一周内需要）
