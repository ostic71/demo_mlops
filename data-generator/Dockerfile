FROM python:3.9-slim

WORKDIR /app

COPY generator.py .

# Không cần package ngoài, có thể bỏ lệnh pip install
# Nếu cần thêm thư viện thì khai báo như bên dưới
# RUN pip install --no-cache-dir numpy pandas

CMD ["python", "generator.py"]
