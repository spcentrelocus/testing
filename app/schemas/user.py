# from pydantic import BaseModel, EmailStr, UUID4
# from typing import Optional

# # Shared properties
# class UserBase(BaseModel):
#     email: EmailStr
#     is_active: Optional[bool] = True
#     role: Optional[str] = "user"

# # Properties to receive via API on creation
# class UserCreate(UserBase):
#     password: str

# # Properties to return via API
# class User(UserBase):
#     id: UUID4
    
#     class Config:
#         from_attributes = True

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenPayload(BaseModel):
#     sub: Optional[str] = None



from pydantic import BaseModel, EmailStr, UUID4, model_validator
from typing import Optional, Any
 
# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    role: Optional[str] = "user"
 
# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    confirm_password: str
 
# Properties to return via API
class User(UserBase):
    id: UUID4
   
    class Config:
        from_attributes = True
 
class UserLogin(BaseModel):
    email: EmailStr
    password: str
 
class Token(BaseModel):
    access_token: str
    token_type: str
 
class TokenPayload(BaseModel):
    sub: Optional[str] = None
 
class APIResponse(BaseModel):
    success: bool
    status: str
    code: int
    message: str
    data: Optional[Any] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
 
class ErrorDetail(BaseModel):
    detail: str
 
class ErrorResponse(BaseModel):
    success: bool = False
    status: str = "error"
    code: int
    message: str
    errors: Optional[Any] = None