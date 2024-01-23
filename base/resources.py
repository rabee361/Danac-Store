from import_export import resources
from .models import *

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        exclude = ('id',)
        
    def get_import_id_fields(self):
        return ['name']