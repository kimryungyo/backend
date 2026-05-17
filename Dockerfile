FROM python:3.12-slim

# 보안을 위해 비루트 사용자를 생성한다.
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

# 의존성 설치 (캐시 활용을 위해 먼저 복사)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 및 소유권 변경
COPY app ./app
RUN chown -R appuser:appgroup /app

# 비루트 사용자로 전환
USER appuser

# 컨테이너 상태 확인을 위한 HEALTHCHECK 추가
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); resp = conn.getresponse(); exit(0) if resp.status == 200 else exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
