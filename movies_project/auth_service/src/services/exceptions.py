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

permission_denied = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action.",
    headers={"WWW-Authenticate": "Bearer"},
)


role_already_exists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Role with this title already exists.",
    headers={"WWW-Authenticate": "Bearer"},
)


def user_already_exists_exception(email: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"User with email {email} already exists",
        headers={"WWW-Authenticate": "Bearer"},
    )


def role_not_found(role_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Role with id {role_id} not found",
        headers={"WWW-Authenticate": "Bearer"},
    )
