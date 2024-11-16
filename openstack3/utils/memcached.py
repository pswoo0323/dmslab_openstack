from pymemcache.client import base

# Memcached 클라이언트 설정
client = base.Client(('127.0.0.1', 11211))

# 특정 키의 값 확인
data = client.get('1234')
print("캐시 데이터:", data.decode('utf-8') if data else "데이터가 없습니다.")
