# 使用一个经过验证的、官方存在的 Python 3.9 slim-buster 版本作为基础
FROM python:3.9-slim-buster

# 更新包列表并安装 lxml 和 pandas 可能需要的系统级编译工具和库
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件，以便利用Docker的缓存机制
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制剩余的应用代码
COPY . .

# 容器启动时运行的命令
# Zeabur会自动检测到端口，我们使用标准命令即可
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]