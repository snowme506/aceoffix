#!/bin/bash
# AceOffix 版本备份脚本
# 用法: ./backup.sh [版本号] 或 ./backup.sh (自动生成时间戳版本)

PROJECT_DIR="/opt/aceoffix"
BACKUP_DIR="/opt/backups/aceoffix"
DATE=$(date +%Y%m%d_%H%M%S)

# 如果提供了版本号，使用它；否则使用时间戳
if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION="v$DATE"
fi

BACKUP_PATH="$BACKUP_DIR/$VERSION"

echo "🔄 备份 AceOffix 项目..."
echo "版本: $VERSION"
echo "源目录: $PROJECT_DIR"
echo "备份目录: $BACKUP_PATH"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 复制项目文件
cp -r "$PROJECT_DIR" "$BACKUP_PATH"

# 记录版本信息
echo "备份时间: $(date)" > "$BACKUP_PATH/version.txt"
echo "版本号: $VERSION" >> "$BACKUP_PATH/version.txt"
echo "备份内容: frontend/ backend/" >> "$BACKUP_PATH/version.txt"

echo "✅ 备份完成: $BACKUP_PATH"
echo ""
echo "📋 备份历史:"
ls -lt "$BACKUP_DIR" | head -10
