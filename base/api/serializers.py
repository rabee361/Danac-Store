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
        request = self.context.get('request')
        user = CustomUser.objects.get(id=request.user.id)
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user


# from django.contrib.auth import get_user_model, authenticate
# from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only = True)

    # class Meta:
        

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)

            if not user:
                try:
                    User = get_user_model()
                    if '@' in username:
                        kwargs = {'email': username}
                    else:
                        kwargs = {'phonenumber': username}
                    user = User.objects.get(**kwargs)
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    pass

            if not user or not user.is_active:
                raise serializers.ValidationError("Incorrect Credentials")
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data

# class UserLoginSerilizer(serializers.ModelSerializer):

#     phonenumber = serializers.CharField()
#     password = serializers.CharField(max_length=55, min_length=6,write_only = True)

#     class Meta:
#         model = CustomUser
#         fields = ['phonenumber', 'password']

#     def validate(self, data):

#         phonenumber = data.get('phonenumber', )
#         password = data.get('password',)

#         if phonenumber is None:
#                 raise serializers.ValidationError({'message_error':'An phonenubmer address is required to log in.'})
        
#         if password is None:
#             raise serializers.ValidationError({'message_error':'A password is required to log in.'})
        
#         user = authenticate(username= phonenumber, password= password)

#         if user is None:
#             raise serializers.ValidationError({'message_error':'A user with this phonenumber and password was not found.'})
        
#         if not user.is_active:
#             raise serializers.ValidationError({'message_error':'This user is not currently activated.'})
        
#         return data
    

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
        model = Point
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
    # products = ProductSerializer()
    class Meta:
        model = Cart_Products
        fields = fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        # return [repr['name'], repr['company']]
        repr['name'] = modify_name(repr['name'])
        # supplier_data = repr.pop('name', 'company')
        return repr
    

class OrderSerializer(serializers.ModelSerializer):
    # products = serializers.ListField(child=serializers.CharField(), write_only=True)
    # products_data = ProductSerializer(source='products', many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    # def create(self, validated_data):
    #     product_names = validated_data.pop('products', [])
    #     order = Order.objects.create(**validated_data)

    #     for product_id in product_names:
    #         try:
    #             product = Product.objects.get(id=product_id)
    #             order.products.add(product)
    #         except Product.DoesNotExist:
    #             raise serializers.ValidationError({'error': f'Product with name {product_id} does not exist'})

    #     order.save()
    #     return order
    

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
        instance.deserved_amount = validated_data.get('deserved_amount', instance.deserved_amount)
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
        instance.num_absence = validated_data.get('num_absence', instance.num_absence)
        instance.amoumt_deducted = validated_data.get('amoumt_deducted', instance.amoumt_deducted)
        instance.save()
        return instance
    

class AwardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Award
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        award = Award.objects.create(employee=employee, **validated_data)
        return award

    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason_award = validated_data.get('reason_award', instance.reason_award)
        instance.total = validated_data.get('total', instance.total)
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
        instance.reason_discount = validated_data.get('reason_discount', instance.reason_discount)
        instance.total = validated_data.get('total', instance.total)
        instance.save()
        return instance
    
class AdvanceSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Advance
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        advance = Advance.objects.create(employee=employee, **validated_data)
        return advance

    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason_advance = validated_data.get('reason_advance', instance.reason_advance)
        instance.total = validated_data.get('total', instance.total)
        instance.save()
        return instance
    
class ExpenseSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = ExtraExpense
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        expense = ExtraExpense.objects.create(employee=employee, **validated_data)
        return expense
    
    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason_expense = validated_data.get('reason_expense', instance.reason_expense)
        instance.total = validated_data.get('total', instance.total)
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


# class MediumSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Medium
#         fields = '__all__'


class ProductsOutputsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outputs_Products
        fields = '__all__'

class OutputsSerializer(serializers.ModelSerializer):
    # products = ProductsOutputsSerializer(read_only=True)
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
    # product = ProductSerializer(many=False, read_only=True)
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

class UpdateReturnGoodSupplierSerializer(serializers.ModelSerializer):
    product = serializers.CharField()
    supplier = serializers.CharField()

    class Meta:
        model = ReturnedGoodsSupplier
        fields = ['product', 'supplier', 'quantity', 'total_price', 'reason']

    def update(self, instance, validated_data):
        product_id = validated_data.pop('product')
        product = Product.objects.get(id=product_id)
        # product.quantity -= validated_data.pop('quantity')
        # product.save()
        supplier_id = validated_data.pop('supplier')
        supplier = Supplier.objects.get(id=supplier_id)
        instance.prodcut = product
        instance.clinet = supplier
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    

class ReturnedGoodsClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnedGoodsClient
        fields = '__all__'

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
        # product.quantity += validated_data.pop('quantity')
        # product.save()
        client_id = validated_data.pop('client')
        client = Client.objects.get(id=client_id)
        instance.prodcut = product
        instance.clinet = client
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

# ------------------------------------------DAMAGED PRODUCTS------------------------------------------

class DamagedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamagedProduct
        fields  ='__all__'


# ---------------------------------------------ORDER ENVOY---------------------------------------------

class OrderEnvoySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderEnvoy
        fields = '__aLL__'


class ProductOrderEnvoySerializer(serializers.ModelSerializer):

    class Meta:
        model = Product_Order_Envoy
        fields = '__all__'


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
