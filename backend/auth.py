"""
Authentication middleware for webhook endpoints
"""
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hmac
import hashlib
import json
from typing import Dict, Any


security = HTTPBearer()

# Get webhook secret from environment variable
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key-change-this-in-production")


async def verify_webhook_signature(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> bool:
    """
    Verify the Bearer token matches the configured webhook secret

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        True if authentication is successful

    Raises:
        HTTPException: If authentication fails
    """
    if credentials.credentials != WEBHOOK_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )
    return True


def generate_webhook_signature(payload: Dict[str, Any], secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload

    Args:
        payload: The webhook payload dictionary
        secret: The shared secret key

    Returns:
        Hexadecimal signature string
    """
    # Convert payload to JSON string with sorted keys for consistency
    payload_string = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return signature


def verify_payload_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    Verify that the payload signature matches the expected signature

    Args:
        payload: The webhook payload dictionary (without the signature field)
        signature: The signature to verify
        secret: The shared secret key

    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(expected_signature, signature)
