# from datetime import timedelta
# from typing import Any
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.api import deps
# from app.core import security
# from app.core.config import settings
# from app.schemas.user import UserCreate, User, Token
# from app.services import user_service

# router = APIRouter()

# @router.post("/register", response_model=User, summary="Register a new user", description="Creates a new user with email and password.")
# async def register(
#     user_in: UserCreate,
#     db: AsyncSession = Depends(deps.get_db),
# ) -> Any:
#     user = await user_service.get_user_by_email(db, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this username already exists in the system.",
#         )
#     user = await user_service.create_user(db, user=user_in)
#     return user

# @router.post("/login", response_model=Token, summary="Login and get Token", description="OAuth2 compatible token login, returns an access token.")
# async def login(
#     db: AsyncSession = Depends(deps.get_db),
#     form_data: OAuth2PasswordRequestForm = Depends()
# ) -> Any:
#     user = await user_service.authenticate_user(
#         db, email=form_data.username, password=form_data.password
#     )
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect email or password")
#     elif not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
    
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     return {
#         "access_token": security.create_access_token(
#             user.email, expires_delta=access_token_expires
#         ),
#         "token_type": "bearer",
#     }



from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate, User, Token, UserLogin, APIResponse, ErrorResponse
from app.services import user_service
 
router = APIRouter()
 
@router.post("/register", response_model=APIResponse, summary="Register a new user", description="Creates a new user with email and password.")
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    if user_in.password != user_in.confirm_password:
        return APIResponse(
            success=False,
            status="error",
            code=status.HTTP_400_BAD_REQUEST,
            message="Registration failed",
            data={"detail": "Passwords do not match."}
        )
       
    user = await user_service.get_user_by_email(db, email=user_in.email)
    if user:
        return APIResponse(
            success=False,
            status="error",
            code=status.HTTP_400_BAD_REQUEST,
            message="Registration failed",
            data={"detail": "The user with this username already exists in the system."}
        )
   
    user = await user_service.create_user(db, user=user_in)
   
    # Generate tokens for the new user
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.email, expires_delta=access_token_expires
    )
    # Using 7 days for refresh token as a standard fallback
    refresh_token_expires = timedelta(days=7)
    refresh_token = security.create_access_token(
        user.email, expires_delta=refresh_token_expires
    )
   
    token_info = {
        "user": User.model_validate(user).model_dump()
    }
   
    return APIResponse(
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=token_info,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
 
@router.post("/login", response_model=APIResponse, summary="Login and get Token", description="Supports both JSON and OAuth2 compatible form login.")
async def login(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    login_data: Optional[UserLogin] = Body(None)
) -> Any:
    # Use username/password from form if available, otherwise use from JSON body
    email = username if username else (login_data.email if login_data else None)
    pwd = password if password else (login_data.password if login_data else None)
 
    # Fallback: if both are None, maybe it's JSON but not matching UserLogin schema prefix
    if not email or not pwd:
        try:
            # Check if it's a raw JSON body that wasn't captured by login_data
            body = await request.json()
            email = email or body.get("email") or body.get("username")
            pwd = pwd or body.get("password")
        except:
            pass
 
    if not email or not pwd:
        return APIResponse(
            success=False,
            status="error",
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Login failed",
            data={"detail": "Email and password are required"}
        )
 
    user = await user_service.authenticate_user(
        db, email=email, password=pwd
    )
    if not user:
        return APIResponse(
            success=False,
            status="error",
            code=status.HTTP_400_BAD_REQUEST,
            message="Login failed",
            data={"detail": "Incorrect email or password"}
        )
    elif not user.is_active:
        return APIResponse(
            success=False,
            status="error",
            code=status.HTTP_400_BAD_REQUEST,
            message="Login failed",
            data={"detail": "Inactive user"}
        )
   
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.email, expires_delta=access_token_expires
    )
   
    # Using 7 days for refresh token as a standard fallback
    refresh_token_expires = timedelta(days=7)
    refresh_token = security.create_access_token(
        user.email, expires_delta=refresh_token_expires
    )
   
    token_data = {
        "user": User.model_validate(user).model_dump()
    }
   
    # Standardized response structure
    response_content = {
        "success": True,
        "status": "success",
        "code": 200,
        "message": "Login successful",
        "data": token_data,
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
   
    return APIResponse(**response_content)