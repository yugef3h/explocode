from fastapi import APIRouter, HTTPException

from app.schemas import AmountPayload, User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])

_users: dict[int, User] = {}
_next_id = 1


@router.get("", response_model=list[User])
def list_users() -> list[User]:
    return list(_users.values())


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    user = _users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=User, status_code=201)
def create_user(payload: UserCreate) -> User:
    global _next_id
    user = User(id=_next_id, name=payload.name, balance=payload.balance)
    _users[_next_id] = user
    _next_id += 1
    return user


@router.post("/{user_id}/charge", response_model=User)
def charge_user(user_id: int, payload: AmountPayload) -> User:
    user = _users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    user.balance -= payload.amount
    return user


@router.post("/{user_id}/refund", response_model=User)
def refund_user(user_id: int, payload: AmountPayload) -> User:
    user = _users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += payload.amount
    return user
