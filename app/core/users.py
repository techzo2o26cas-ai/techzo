from pydantic import BaseModel,EmailStr,Field,field_validator
import re

class NewUser(BaseModel):
    name:str
    email:EmailStr
    password:str


    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain a number")

        if not re.search(r"[!@#$%^&*()]", v):
            raise ValueError("Password must contain special character")

        return v
    


