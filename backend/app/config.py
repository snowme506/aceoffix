import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/aceoffix.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "aceoffix-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# JWT Config
JWT_CONFIG = {
    "secret_key": SECRET_KEY,
    "algorithm": ALGORITHM,
    "expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
}

# Mock SMS (for development)
MOCK_SMS_CODE = "1234"
SMS_CODE_EXPIRE_MINUTES = 60  # 固定验证码用于测试

# Points Config
POINTS_CONFIG = {
    "register_bonus": 100,  # 注册赠送积分
    "order_ratio": 1.0,     # 消费1元得1积分
    "referral_bonus": 50,   # 推荐奖励积分
}
