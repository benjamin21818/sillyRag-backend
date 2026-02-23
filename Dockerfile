FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如果需要）
# RUN apt-get update && apt-get install -y --no-install-recommends ...

COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
