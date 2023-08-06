from serene.resources import ModelResource
from serene.tests.models import Brand, Product

class BrandResource(ModelResource):
    model = Brand

class ProductResource(ModelResource):
    model = Product