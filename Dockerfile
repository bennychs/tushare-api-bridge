# 使用官方的 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 更新包列表并安装 lxml 所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制剩余的应用代码
COPY . .

# 暴露应用运行的端口
EXPOSE 8000

# 容器启动时运行的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
