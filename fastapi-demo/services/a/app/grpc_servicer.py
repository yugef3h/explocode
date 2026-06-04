import sys
from pathlib import Path

import grpc
from redis_om import NotFoundError

_DEMO_ROOT = Path(__file__).resolve().parents[3]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))

from product.v1 import product_pb2, product_pb2_grpc

from app.inventory import InsufficientStockError, release_stock, reserve_stock
from app.models import Product
from app.schemas import ProductCreate


def _to_proto(product: Product) -> product_pb2.Product:
    return product_pb2.Product(
        id=product.pk,
        name=product.name,
        price=product.price,
        quantity=product.quantity,
    )


class ProductServicer(product_pb2_grpc.ProductServiceServicer):
    def GetProduct(self, request, context):
        try:
            return _to_proto(Product.get(request.product_id))
        except NotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")

    def ListProducts(self, request, context):
        products = [_to_proto(Product.get(pk)) for pk in Product.all_pks()]
        return product_pb2.ListProductsResponse(products=products)

    def CreateProduct(self, request, context):
        payload = ProductCreate(
            name=request.name,
            price=request.price,
            quantity=request.quantity,
        )
        product = Product(pk=None, **payload.model_dump()).save()
        return _to_proto(product)

    def ReserveStock(self, request, context):
        try:
            remaining = reserve_stock(request.product_id, request.quantity)
        except NotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")
        except InsufficientStockError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Insufficient product stock")
        return product_pb2.StockResponse(id=request.product_id, quantity=remaining)

    def ReleaseStock(self, request, context):
        try:
            remaining = release_stock(request.product_id, request.quantity)
        except NotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")
        return product_pb2.StockResponse(id=request.product_id, quantity=remaining)

    def DeleteProduct(self, request, context):
        try:
            Product.get(request.product_id)
        except NotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")
        Product.delete(request.product_id)
        return product_pb2.DeleteProductResponse(
            status="ok",
            message="Product deleted successfully",
        )

    def HealthCheck(self, request, context):
        return product_pb2.HealthCheckResponse(
            status="ok",
            service="a-service",
            redis="ok",
        )
