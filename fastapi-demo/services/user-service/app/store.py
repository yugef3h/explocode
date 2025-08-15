from app.schemas import User, UserCreate


class UserNotFoundError(Exception):
    pass


class InsufficientBalanceError(Exception):
    pass


_users: dict[int, User] = {}
_next_id = 1


def list_users() -> list[User]:
    return list(_users.values())


def get_user(user_id: int) -> User:
    user = _users.get(user_id)
    if user is None:
        raise UserNotFoundError()
    return user


def create_user(payload: UserCreate) -> User:
    global _next_id
    user = User(id=_next_id, name=payload.name, balance=payload.balance)
    _users[_next_id] = user
    _next_id += 1
    return user


def charge_user(user_id: int, amount: float) -> User:
    user = get_user(user_id)
    if user.balance < amount:
        raise InsufficientBalanceError()
    user.balance -= amount
    return user


def refund_user(user_id: int, amount: float) -> User:
    user = get_user(user_id)
    user.balance += amount
    return user
