from openstack import connection
from django.core.cache import cache
from django.conf import settings


def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn

TOKEN_CACHE_TIMEOUT = 3600

def get_cached_openstack_token(user_id):
    # 캐시에서 토큰 가져오기
    token = cache.get(f"openstack_token_{user_id}")

    if token:
        print(f"캐시에서 토큰을 가져왔습니다: {token}")
        return token

    # 캐시에 토큰이 없거나 만료된 경우, OpenStack에서 새로 발급
    conn = connection.from_config(cloud_name='default')
    token = conn.authorize()  # authorize()를 통해 인증 토큰을 생성 및 가져옴

    # 토큰을 캐시에 저장
    cache.set(f"openstack_token_{user_id}", token, TOKEN_CACHE_TIMEOUT)
    print(f"새 토큰이 발급되어 캐시에 저장되었습니다: {token}")
    return token