#!/bin/bash
# AceOffix 发布脚本 - 支持预览和发布
# 用法: ./deploy.sh preview 或 ./deploy.sh publish

PROJECT_DIR="/opt/aceoffix"
BACKUP_DIR="/opt/backups/aceoffix"
PREVIEW_DIR="/opt/aceoffix/preview"
DATE=$(date +%Y%m%d_%H%M%S)
VERSION="v$(date +%Y%m%d)"

if [ "$1" == "preview" ]; then
    echo "🔄 部署到预览环境..."
    
    # 备份当前生产版本
    if [ ! -d "$BACKUP_DIR/$VERSION" ]; then
        echo "📦 备份当前版本: $VERSION"
        cp -r "$PROJECT_DIR/frontend" "$BACKUP_DIR/$VERSION"
        echo "备份时间: $(date)" > "$BACKUP_DIR/$VERSION/version.txt"
    fi
    
    # 同步到预览目录
    rsync -av "$PROJECT_DIR/frontend/" "$PREVIEW_DIR/" --exclude=preview
    
    echo "✅ 预览环境已更新: http://101.201.181.170/preview/"
    echo "📝 请检查预览效果，确认后执行: ./deploy.sh publish"
    
elif [ "$1" == "publish" ]; then
    echo "🚀 发布到生产环境..."
    
    # 备份当前生产版本
    BACKUP_NAME="${VERSION}_$(date +%H%M%S)"
    echo "📦 备份生产版本: $BACKUP_NAME"
    cp -r "$PROJECT_DIR/frontend" "$BACKUP_DIR/$BACKUP_NAME"
    echo "备份时间: $(date)" > "$BACKUP_DIR/$BACKUP_NAME/version.txt"
    echo "类型: 生产版本" >> "$BACKUP_DIR/$BACKUP_NAME/version.txt"
    
    # 从预览目录发布到生产
    rsync -av "$PREVIEW_DIR/" "$PROJECT_DIR/frontend/"
    
    echo "✅ 生产环境已发布: http://101.201.181.170/"
    echo "📋 版本历史:"
    ls -lt "$BACKUP_DIR" | head -10
    
elif [ "$1" == "rollback" ]; then
    echo "↩️  回滚到上一版本..."
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "恢复备份: $LATEST_BACKUP"
        rm -rf "$PROJECT_DIR/frontend"
        cp -r "$BACKUP_DIR/$LATEST_BACKUP" "$PROJECT_DIR/frontend"
        echo "✅ 已回滚到: $LATEST_BACKUP"
    else
        echo "❌ 没有找到备份"
    fi
    
else
    echo "用法:"
    echo "  ./deploy.sh preview  - 部署到预览环境"
    echo "  ./deploy.sh publish  - 发布到生产环境"
    echo "  ./deploy.sh rollback - 回滚到上一版本"
fi
