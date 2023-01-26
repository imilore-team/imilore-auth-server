from os import environ
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError

from src.init import db
from src.models.auth import UserAuthModel
from src.tables.auth import UserAuth


class AuthProvider:
    hasher = CryptContext(schemes=['bcrypt'])
    security = HTTPBearer()

    SECRET_KEY = environ["SECRET_KEY"]
    ALGORITHM = environ["ALGORITHM"]
    ACCESS_LIFETIME = timedelta(minutes=int(environ["ACCESS_LIFETIME"]))
    RENEW_LIFETIME = timedelta(minutes=int(environ["RENEW_LIFETIME"]))

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token. Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    scope_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect token scope",
        headers={"WWW-Authenticate": "Bearer"},
    )


    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.hasher.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.hasher.verify(plain_password, hashed_password)

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> UserAuthModel | None:
        user = db.get(value=email, by=UserAuth.email, object=UserAuth)
        if user is None:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None

        return user

    @classmethod
    def encode_token(cls, data: dict) -> str:
        return jwt.encode(data, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> str:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            
            if payload["scope"] == "access":
                return payload['sub']
            
            raise cls.scope_exception
        except ExpiredSignatureError:
            raise cls.expired_exception
        except JWTError:
            raise cls.credentials_exception

    @classmethod
    def renew_token(cls, token: str) -> str:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            if payload["scope"] == "refresh":
                subject = payload["sub"]
                token = cls.create_token({"sub": subject})
                
                return token
            
            raise cls.scope_exception
        except ExpiredSignatureError:
            raise cls.expired_exception
        except JWTError:
            raise cls.credentials_exception


    @classmethod
    def create_token(cls, data: dict, lifetime: timedelta | None = None, scope="access") -> str:
        to_encode = data.copy()

        now = datetime.utcnow()
        to_encode["iat"] = now

        if lifetime is not None:
            expire = now + lifetime
        else:
            expire = now + cls.ACCESS_LIFETIME
        to_encode["exp"] = expire
        
        to_encode["scope"] = scope

        encoded_jwt = cls.encode_token(to_encode)
        
        return encoded_jwt

    @classmethod
    def create_user_tokens(cls, user: UserAuthModel) -> dict[str, str]:
        access_token = cls.create_token({"sub": user.email})
        refresh_token = cls.create_token(
            {"sub": user.email}, 
            lifetime=cls.RENEW_LIFETIME, 
            scope="refresh"
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    @classmethod
    def get_token(cls, credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        return token