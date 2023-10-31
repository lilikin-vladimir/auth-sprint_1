from fastapi import HTTPException, status


wrong_username_or_password_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

relogin_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Your credentials expired. Please login again.",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_access_token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. "
                   "Create new token with /refresh",
            headers={"WWW-Authenticate": "Bearer"},
)


def user_already_exists_exception(email: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"User with email {email} already exists",
        headers={"WWW-Authenticate": "Bearer"},
    )
