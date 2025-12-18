import httpx
from fastapi import Request, HTTPException, Depends
from typing import Optional
import os
from auth_models import User

LARAVEL11_URL = os.getenv("LARAVEL11_URL", "http://localhost/v2")
LARAVEL9_URL = os.getenv("LARAVEL9_URL", "http://localhost")

async def get_current_user(request: Request) -> Optional[User]:
    """Extract and validate user from Laravel session cookies"""
    cookies = request.cookies

    # Try Laravel 11 first
    l11_cookie = cookies.get('laravel11_session')
    if l11_cookie:
        user = await validate_session(LARAVEL11_URL, l11_cookie, 'laravel11_session')
        if user:
            return user

    # Try Laravel 9
    l9_cookie = cookies.get('digital_operations_session')
    if l9_cookie:
        user = await validate_session(LARAVEL9_URL, l9_cookie, 'digital_operations_session')
        if user:
            return user

    return None

async def validate_session(base_url: str, cookie: str, cookie_name: str) -> Optional[User]:
    """Call Laravel API to validate session"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/session/validate",
                cookies={cookie_name: cookie},
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    user_data = data['user']
                    return User(
                        id=user_data['id'],
                        email=user_data['email'],
                        name=user_data['name'],
                        source_system=data['source_system'],
                        is_admin=user_data['is_admin'],
                        department=user_data.get('department'),
                        roles=user_data.get('roles', [])
                    )
    except Exception as e:
        print(f"Session validation error for {base_url}: {e}")

    return None

async def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication"""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return user
