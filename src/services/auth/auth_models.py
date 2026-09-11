from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthUser:
    uid: str
    email: str = ""
    display_name: str = ""
    photo_url: str = ""
    phone_number: str = ""
    id_token: str = ""
    refresh_token: str = ""
    expires_in: int = 3600
    email_verified: bool = False


@dataclass
class AuthResult:
    success: bool
    message: str
    user: Optional[AuthUser] = None
