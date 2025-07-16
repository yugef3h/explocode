from redis_om import HashModel

ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_COMPLETED = "completed"


class Order(HashModel):
    user_id: int
    product_id: str
    item: str
    amount: float
    quantity: int
    status: str = ORDER_STATUS_PENDING

    class Meta:
        global_key_prefix = "order"
