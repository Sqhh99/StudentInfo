#!/bin/bash

# 设置终端颜色
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> 清理旧容器...${NC}"
docker-compose down

echo -e "${GREEN}>>> 开始构建镜像...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}>>> 构建完成！${NC}"

read -p "是否要立即启动服务？(y/n) " start_service

if [ "$start_service" = "y" ] || [ "$start_service" = "Y" ]; then
    echo -e "${GREEN}>>> 启动服务...${NC}"
    docker-compose up -d
    echo -e "${GREEN}>>> 可以使用 'docker-compose logs -f' 查看日志${NC}"
else
    echo -e "${GREEN}>>> 您可以使用 'docker-compose up -d' 启动服务${NC}"
fi 