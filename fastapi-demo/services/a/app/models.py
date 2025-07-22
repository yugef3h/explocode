from redis_om import HashModel


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        global_key_prefix = "product"
