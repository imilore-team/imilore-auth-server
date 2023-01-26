from fastapi import APIRouter, HTTPException, status, Depends

from src.init import db
from src.models.auth import UserAuthModel, InUserAuthModel
from src.tables.auth import UserAuth
from src.providers.auth import AuthProvider


router = APIRouter()


@router.post("/register")
def post_register(userIn: InUserAuthModel) -> dict[str, str]:
    user = UserAuth(
        email=userIn.email, 
        hashed_password=AuthProvider.hash_password(userIn.password)
    )
    db.add(user)

    tokens = AuthProvider.create_user_tokens(UserAuthModel(email=userIn.email))
    return tokens

@router.post("/login")
def post_login(userIn: InUserAuthModel) -> dict[str, str]:
    user = AuthProvider.authenticate_user(userIn.email, userIn.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = AuthProvider.create_user_tokens(user)

    return tokens


@router.get("/refresh_token")
def get_refresh_token(token: str = Depends(AuthProvider.get_token)) -> str:
    return AuthProvider.renew_token(token)