from redis_om import HashModel


class Order(HashModel):
    user_id: int
    item: str
    amount: float

    class Meta:
        global_key_prefix = "order"
