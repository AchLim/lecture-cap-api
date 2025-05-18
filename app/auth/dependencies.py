from fastapi import Request, HTTPException, Depends
from firebase_admin import auth, exceptions

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")

    token = auth_header.split(" ")[1]
    try:
        # Verifies the token and returns user claims
        decoded_token = auth.verify_id_token(token, clock_skew_seconds=60)
        return decoded_token
    except exceptions.FirebaseError as e:
        # Firebase-specific exception handling
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    except Exception:
        # Catch-all for any unexpected errors
        raise HTTPException(status_code=401, detail="Token verification failed")