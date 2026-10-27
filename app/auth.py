import os
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def require_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Check the username and password sent in the Authorization header."""
    expected_user = os.getenv("API_USERNAME", "teacher")
    expected_pass = os.getenv("API_PASSWORD", "change-me-123")

    # compare_digest takes the same time for right and wrong guesses
    user_ok = secrets.compare_digest(credentials.username.encode(), expected_user.encode())
    pass_ok = secrets.compare_digest(credentials.password.encode(), expected_pass.encode())

    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
