"""FastAPI Routes for User Authentication and Role-Based Access Control (RBAC)."""
import json
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Header, Depends
from app.mcp_client import MCPDatabaseClient

router = APIRouter(prefix="/api/auth", tags=["User Authentication & RBAC API"])
mcp_client = MCPDatabaseClient()


class LoginRequest(BaseModel):
    """Payload for user authentication."""
    username: str = Field(..., description="Account username ('admin' or 'user')")
    password: str = Field(..., description="Account password ('admin123' or 'user123')")


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate user credentials via MCP Database Tool.
    
    Returns user profile payload containing username, role ('admin' or 'user'),
    and authentication token.
    """
    try:
        res = await mcp_client.call_tool("authenticate_user", {
            "username": req.username.strip(),
            "password": req.password.strip()
        })

        if res.get("status") != "success":
            raise HTTPException(status_code=401, detail="Invalid username or password.")

        role = res.get("role", "user")

        return {
            "status": "success",
            "message": f"Successfully logged in as {role.upper()}.",
            "user": {
                "username": res.get("username"),
                "role": role,
                "token": f"token_{res.get('username')}_{role}"
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@router.post("/logout")
async def logout():
    """Sign out user session."""
    return {"status": "success", "message": "Successfully logged out."}


@router.get("/me")
async def get_current_user_profile(
    authorization: Optional[str] = Header(None, description="Optional Bearer token header")
):
    """Fetch active session profile."""
    if authorization and "admin" in authorization:
        return {"status": "success", "user": {"username": "admin", "role": "admin"}}
    elif authorization and "user" in authorization:
        return {"status": "success", "user": {"username": "user", "role": "user"}}
    
    # Default fallback profile
    return {"status": "success", "user": {"username": "user", "role": "user"}}
