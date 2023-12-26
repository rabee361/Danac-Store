from rest_framework import serializers
from base.models import *
from django.contrib.auth import login
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import TokenError, RefreshToken

from django.contrib.auth.password_validation import validate_password


def modify_name(name):
    return name

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'phonenumber', 'password', 'image']


class CodeVerivecationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVerivecation
        fields = '__all__'

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['image']

    def update(self, instance, validated_data):
        instance.image = validated_data['image']
        instance.save()
        return instance


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['phonenumber', 'email', 'username', 'password']

        extra_kwargs = {
            'password':{'write_only':True,}
        }

        def validate(self, validated_data):
            validate_password(validated_data['password'])
            return validated_data

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        user = CustomUser(
            phonenumber=self.validated_data['phonenumber'],
            email = self.validated_data['email'],
            username = self.validated_data['username']
        )
        password = self.validated_data['password']
        user.set_password(password)
        # user.is_active = False
        user.save()
        return user

################################
class ResetPasswordSerializer(serializers.ModelSerializer):

    newpassword = serializers.CharField(style={"input_type":"password"}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ['password', 'newpassword']

        extra_kwargs = {
            'password':{'write_only':True,}
        }

    def validate(self, attrs):
        password = attrs.get('password', '')
        newpassword = attrs.get('newpassword', '')
        validate_password(password)
        validate_password(newpassword)
        
        if password != newpassword:
            raise serializers.ValidationError({'message_error':'The password and newpassword didnt matched.'})
        
        return attrs
    
    def save(self, **kwargs):
        user_id = self.context.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        password = self.validated_data['newpassword']
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user or not user.is_active:
                raise serializers.ValidationError("Incorrect Credentials")
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Points
        fields = '__all__'

            
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        category = Category.objects.get(name=category_name)
        product = Product.objects.create(category=category, **validated_data)
        return product

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        repr['category'] = instance.category.name
        return repr
        
    def update(self, instance, validated_data):
        category_name = validated_data.pop('category')
        category = Category.objects.get(name=category_name)
        instance.category = validated_data.get('category', category)
        instance.name = validated_data.get('name', instance.name)
        instance.iamge = validated_data.get('iaage', instance.iamge)
        instance.description = validated_data.get('description', instance.description)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.purch_price = validated_data.get('purch_price', instance.purch_price)
        instance.sale_price = validated_data.get('sale_price', instance.sale_price)
        instance.num_per_item = validated_data.get('num_per_item', instance.num_per_item)
        instance.item_per_carton = validated_data.get('item_per_carton', instance.item_per_carton)
        instance.limit = validated_data.get('limit', instance.limit)
        instance.info = validated_data.get('info', instance.info)
        instance.added = validated_data.get('added', instance.added)
        instance.save()
        return instance

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
 

class Cart_ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Products
        fields = fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr
    

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class OverTimeSerializer(serializers.ModelSerializer):

    employee = serializers.CharField()
    class Meta:
        model = OverTime
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        overtime = OverTime.objects.create(employee=employee, **validated_data)
        return overtime

    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.num_hours = validated_data.get('num_hours', instance.num_hours)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance

class AbsenceSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Absence
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        absence = Absence.objects.create(employee=employee, **validated_data)
        return absence
    
    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.days = validated_data.get('days', instance.days)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    

class AwardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Bonus
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        award = Bonus.objects.create(employee=employee, **validated_data)
        return award

    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    
class DiscountSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Discount
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        discount = Discount.objects.create(employee=employee, **validated_data)
        return discount
    
    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    
class AdvanceSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Advance_On_salary
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        advance = Advance_On_salary.objects.create(employee=employee, **validated_data)
        return advance

    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
    
class ExpenseSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Extra_Expense
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        expense = Extra_Expense.objects.create(employee=employee, **validated_data)
        return expense
    
    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.barcode = validated_data.get('barcode', instance.barcode)
        instance.save()
        return instance

class IncomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming
        fields = '__all__'
    
    
class IncomingProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming_Product
        fields = '__all__'


class ManualRecieptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualReceipt
        fields = '__all__'

    
class ManualRecieptProductsSerializer(serializers.ModelSerializer):
    class Meta :
        model = ManualReceipt_Products
        fields = '__all__'


class ProductsOutputsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outputs_Products
        fields = '__all__'

class OutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputs
        fields = '__all__'

class GetOutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputs
        fields = ['client', 'employee', 'verify_code', 'phonenumber', 'recive_pyement', 'discount', 'Reclaimed_products', 'previous_depts', 'remaining_amount', 'date']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['client'] = instance.client.name
        repr['id'] = instance.client.id
        repr['employee'] = instance.employee.name
        return repr
    
class GetProductsOutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputs_Products
        fields = ['products', 'quantity', 'total', 'discount']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['num_per_item '] = instance.products.num_per_item
        repr['sale_price'] = instance.products.sale_price
        repr['product'] = instance.products.name
        return repr


class DelevaryArrivedSerializer(serializers.ModelSerializer):
    output_receipt = OutputsSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = DelevaryArrived
        fields = '__all__'


# --------------------------------------CREATE MEDIUM--------------------------------------
class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        models = Medium
        fields = '__all__'

class ProductsMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products_Medium
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['num_per_item '] = instance.product.num_per_item
        repr['sale_price'] = instance.product.sale_price
        repr['product'] = instance.product.name
        return repr

class UpdateProductMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products_Medium
        fields = ['discount']
# ------------------------------------------RETURNED GOODS------------------------------------------
    
class ReturnedGoodsSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedGoodsSupplier
        fields = '__all__'

    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['supplier'] = instance.supplier.name
        reper['employee'] = instance.employee.name
        reper['product'] = instance.product.name
        return reper

class UpdateReturnGoodSupplierSerializer(serializers.ModelSerializer):
    product = serializers.CharField()
    supplier = serializers.CharField()

    class Meta:
        model = ReturnedGoodsSupplier
        fields = ['product', 'supplier', 'quantity', 'total_price', 'reason']

    def update(self, instance, validated_data):
        product_id = validated_data.pop('product')
        product = Product.objects.get(id=product_id)
        supplier_id = validated_data.pop('supplier')
        supplier = Supplier.objects.get(id=supplier_id)
        instance.prodcut = product
        instance.clinet = supplier
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['supplier'] = instance.supplier.name
        reper['employee'] = instance.employee.name
        reper['product'] = instance.product.name
        return reper

class ReturnedGoodsClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnedGoodsClient
        fields = '__all__'

    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['client'] = instance.client.name
        reper['employee'] = instance.employee.name
        reper['product'] = instance.product.name
        return reper

class UpdateReturnedGoodsClientSerializer(serializers.ModelSerializer):

    product = serializers.CharField()
    client = serializers.CharField()
    quantity = serializers.IntegerField()

    class Meta:
        model = ReturnedGoodsClient
        fields = ['product', 'client', 'quantity', 'total_price', 'reason']

    def update(self, instance, validated_data):
        product_id = validated_data.pop('product')
        product = Product.objects.get(id=product_id)
        client_id = validated_data.pop('client')
        client = Client.objects.get(id=client_id)
        instance.prodcut = product
        instance.clinet = client
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['client'] = instance.client.name
        reper['employee'] = instance.employee.name
        reper['product'] = instance.product.name
        return reper

# ------------------------------------------DAMAGED PRODUCTS------------------------------------------

class DamagedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamagedProduct
        fields  ='__all__'


# ---------------------------------------------ORDER ENVOY---------------------------------------------

class OrderEnvoySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderEnvoy
        fields = '__all__'

class ListOrderEnvoySerialzier(serializers.ModelSerializer):
    class Meta : 
        model = OrderEnvoy
        fields = ['client', 'phonenumber', 'products_num', 'total_price', 'delivery_date']


class ProductOrderEnvoySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Order_Envoy
        fields = '__all__'

    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['product'] = instance.product.name
        reper['image'] = instance.product.image.url
        reper['sale_price'] = instance.product.sale_price
        reper['description'] = instance.product.description

        return reper


class MediumTwoSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediumTwo
        fields = '__all__'


class MediumTwo_ProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediumTwo_Products
        fields = '__all__'

    def to_representation(self, instance):
        reper = super().to_representation(instance)
        request = self.context.get('request')
        reper['product'] = instance.product.name
        reper['image'] = instance.product.image.url
        reper['sale_price'] = instance.product.sale_price
        reper['description'] = instance.product.description

        return reper
