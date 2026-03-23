import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import uuid


def encode(user):
    
    access_payload={
        'user_id':user.id,
        'email':user.email,
        'exp':datetime.utcnow()+settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        'iat':datetime.utcnow(),
        'type':'access'
    }

    refresh_payload={
        'user_id':user.id,
        'email':user.email,
        'exp':datetime.utcnow()+settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        'iat':datetime.utcnow(),
        'token_type':'refresh',
        "jti": str(uuid.uuid4()),

    }

    access_token=jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm='HS256'

    )
    refresh_token=jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm='HS256',
    )

    return {
        'access':access_token,
        'refresh':refresh_token
    }




def decode(model,request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise AuthenticationFailed("Authorization header missing")

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationFailed("Bearer token not provided")

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
            )
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired")   #while secret key not match
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")   #signature wrong / tampered / invalid format
    
    if payload.get("type") != 'access':
        raise AuthenticationFailed("Invalid Token")
    user_id=payload.get("user_id")
    user=model.objects.filter(id=user_id).first()
    if not user:
        raise AuthenticationFailed("Token User not found")
    
    return (user,token)


