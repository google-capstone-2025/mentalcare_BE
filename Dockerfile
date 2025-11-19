FROM python:3.10-slim

# 작업 디렉토리 생성
WORKDIR /app

# 요구사항 복사 및 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 복사
COPY . .

# FastAPI 실행 (Compose가 command로 override 가능)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
