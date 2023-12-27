from rest_framework import serializers
from base.models import *
from django.contrib.auth import login , authenticate , get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.serializers import StringRelatedField
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


############################################################## AUTHENTICATION ###################################################

def modify_name(name):
    return name

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'phonenumber', 'password', 'image']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['image']

    def update(self, instance, validated_data):
        instance.image = validated_data['image']
        instance.save()
        return instance
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError("Incorrect Credentials")
            if not user.is_active:
                raise serializers.ValidationError({'message_error':'this account is not active'})
            if not user.is_verified:
                raise serializers.ValidationError({'message_error':'this account is not verified'})
            if not user.is_accepted:
                raise serializers.ValidationError({'message_error':'this account is not accepted'})
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data



class SignUpSerializer(serializers.ModelSerializer):
    x = serializers.FloatField(write_only=True)
    y = serializers.FloatField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['phonenumber', 'email', 'username', 'password','x','y']
        extra_kwargs = {
            'password':{'write_only':True,}
        }
        def validate(self, validated_data):
            validate_password(validated_data['password'])
            return validated_data

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        x = self.validated_data['x']
        y = self.validated_data['y']
        user = CustomUser(
            phonenumber=self.validated_data['phonenumber'],
            email = self.validated_data['email'],
            username = self.validated_data['username'],
            location = Point(x,y)
        )
        password = self.validated_data['password']

        user.set_password(password)
        user.is_active = False
        user.save()
        return user




class SerializerNotificationI(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'
    def to_representation(self, instance):
        reper = super().to_representation(instance)
        reper['username'] = instance.user.username
        return reper



class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')



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


class CodeVerivecationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVerification
        fields = '__all__'

############################################################### PRODUCT AND CLIENTS AND ORDERS ###########################################


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class ClientSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = ['id','name', 'address', 'phonenumber', 'category', 'notes', 'location', 'total_points']

    def get_total_points(self,obj):
        total = Points.objects.filter(Q(client=obj)&Q(is_used=False)&Q(expire_date__gt=timezone.now())).aggregate(total_points=models.Sum('number'))['total_points'] or 0
        return total




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
    
    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({"category": "Object with name does not exist."})
        return super(ProductSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        repr['category'] = instance.category.name
        return repr



class Product2Serializer(serializers.ModelSerializer):
    category = serializers.CharField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        category = Category.objects.get(name=category_name)
        product = Product.objects.create(category=category, **validated_data)
        return product
    
    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({"category": "Object with name does not exist."})
        return super(ProductSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        repr['category'] = instance.category.name
        return repr



class Product3Serializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id','name','image','description','sale_price']

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)




class Cart_ProductsSerializer(serializers.ModelSerializer):
    products = Product3Serializer()
    class Meta:
        model = Cart_Products
        fields = ['id','quantity','cart','products','total_price_of_item']

class Cart_ProductsSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Cart_Products
        fields = '__all__'



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id','customer','items','get_items_num','total_cart_price']




class OrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_Product
        fields = ['product','order','quantity','total_price']



class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    products = OrderProductsSerializer(source='order_product_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'products', 'total', 'products_num', 'created', 'delivery_date', 'delivered']



class OrderProductsSerializer2(serializers.ModelSerializer):
    image = serializers.ImageField(source='product.image')
    description = serializers.CharField(source='product.description')
    class Meta:
        model = Order_Product
        fields = ['product','order','quantity','total_price','image','description']



class OrderSerializer2(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='client.id')
    name = serializers.CharField(source='client.name')
    address = serializers.CharField(source='client.address')
    phonenumber = serializers.CharField(source='client.phonenumber')
    products = OrderProductsSerializer2(source='order_product_set', many=True)
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['client_id','address','name','phonenumber','products','total','products_num','created','longitude','latitude']

    def get_longitude(self, obj):
        return obj.client.location.x or 0

    def get_latitude(self, obj):
        return obj.client.location.y or 0
    


class SimpleOrderSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='client.id')
    name = serializers.CharField(source='client.name')
    class Meta:
        model = Order
        fields = ['client_id','id','name','total','products_num']


################################################################################################################

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class SalesEmployeeSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        fields = ['id','name','notes','truck_num','phonenumber','longitude','latitude','address']

    def get_longitude(self, obj):
        return obj.location.x

    def get_latitude(self, obj):
        return obj.location.y




class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id','name','company_name','address','phone_number','info']
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr
    

############################################################## HR ##################################################################

class Advance_on_SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Advance_On_salary
        fields = '__all__'



class OverTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverTime
        fields = '__all__'


class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = '__all__'


class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = '__all__'
    

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class ExtraExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra_Expense
        fields = '__all__'





class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name']


class SalarySerializer(serializers.ModelSerializer):
    hr = SimpleEmployeeSerializer(many=False,read_only=True)
    class Meta:
        model = Salary
        fields = '__all__'



class EmployeeSalarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ['id','job_position','name', 'salary','sale_percentage']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        related_models = [
            'overtime_set',
            'absence_set',
            'bonus_set',
            'discount_set',
            'advance_on_salary_set',
            'extra_expense_set',
        ]

        totals = {}
        for related_model in related_models:
            related_objects = getattr(instance, related_model).all()
            total = sum(obj.amount for obj in related_objects)
            totals[related_model] = total
            representation[related_model] = total

        total = instance.salary - totals['advance_on_salary_set'] - totals['extra_expense_set'] - totals['absence_set'] - totals['discount_set'] + totals['overtime_set'] + totals['bonus_set'] + (instance.salary * instance.sale_percentage)
        representation['total'] = total
        return representation

#########################################################################################################




############################################################# Registry ##############################################################

class RegistrySerializer(serializers.ModelSerializer):
    class Meta :
        model = Registry
        fields = ['total']


class Client_DebtSerializer(serializers.ModelSerializer):
    total_client_debts = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    class Meta :
        model = Debt_Client
        fields = '__all__'

    def get_total_client_debts(self, obj):
        return Debt_Client.get_total_client_debts()

    def get_total_sum(self, obj):
        return Debt_Client.get_total_sum()



class Supplier_DebtSerializer(serializers.ModelSerializer):
    total_supplier_debts = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    class Meta :
        model = Debt_Supplier
        fields = '__all__'

    def get_total_supplier_debts(self, obj):
        return Debt_Supplier.get_total_supplier_debts()

    def get_total_sum(self, obj):
        return Debt_Supplier.get_total_sum()



class DepositeSerializer(serializers.ModelSerializer):
    total_deposites = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    class Meta:
        model = Deposite
        fields = '__all__'

    def get_total_deposites(self, obj):
        return Deposite.get_total_deposites()

    def get_total_sum(self, obj):
        return Deposite.get_total_sum()



class WithDrawSerializer(serializers.ModelSerializer):
    total_withdraws = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    class Meta:
        model = WithDraw
        fields = '__all__'

    def get_total_withdraws(self, obj):
        return WithDraw.get_total_withdraws()

    def get_total_sum(self, obj):
        return WithDraw.get_total_sum()



class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class RecievedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recieved_Payment
        fields = '__all__'

#################################################### Medium #######################################################################3###



class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = '__all__'

class ProductsMediumSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False,read_only=True)
    class Meta:
        model = Products_Medium
        fields = '__all__'
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['num_per_item'] = instance.product.num_per_item
        repr['sale_price'] = instance.product.sale_price
        repr['product'] = instance.product.name
        return repr

class UpdateProductMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products_Medium
        fields = ['discount']



######################################## RETURNED GOODS #####################################################################




# class ProductSerializerGoods(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ['name']  # include other fields if needed

# class SupplierSerializerGoods(serializers.ModelSerializer):
#     class Meta:
#         model = Supplier
#         fields = ['name']  # include other fields if needed

# class EmployeeSerializerGoods(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = ['name'] 

# class ClientSerializerGoods(serializers.ModelSerializer):
#     class Meta:
#         model = Client
#         fields = ['name'] 


class ReturnedGoodsClientSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    class Meta:
        model = ReturnedGoodsClient
        fields = ['id','client','product','employee','quantity','total_price','reason','date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        representation['client'] = instance.client.name
        representation['employee'] = instance.employee.name
        return representation



class ReturnedGoodsSupplierSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    class Meta:
        model = ReturnedGoodsSupplier
        fields = ['id', 'supplier', 'product', 'employee', 'quantity', 'total_price', 'reason', 'date']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        representation['supplier'] = instance.supplier.name
        representation['employee'] = instance.employee.name
        return representation

    
############################################# DAMAGED PRODUCTS #########################################################

class DamagedProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = DamagedProduct
        fields  = ['id','product','quantity','total_price','date','product_id']

    def update(self, instance, validated_data):
        original_quantity = instance.quantity
        super().update(instance, validated_data)
        quantity_diff = original_quantity - instance.quantity
        product = instance.product
        product.quantity += quantity_diff
        product.save()

        return instance
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        product = instance.product
        product.quantity -= instance.quantity
        product.save()

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        return representation

    


class PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Points
        fields = '__all__'




#################################################### RECIEPTS ###################################################################



################################# INCOMING ############################################# 


class IncomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming
        fields = '__all__'
    


class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','num_per_item','sale_price']



class IncomingProductsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    num_per_item = serializers.IntegerField(source='product.num_per_item')
    sale_price = serializers.FloatField(source='product.sale_price')

    class Meta:
        model = Incoming_Product
        fields = ['id', 'name', 'num_per_item', 'sale_price', 'num_item', 'total_price', 'incoming']



class IncomingSerializer2(serializers.ModelSerializer):
    products = IncomingProductsSerializer(source='incoming_product_set', many=True,read_only=True)
    class Meta:
        model = Incoming
        fields = ['id','agent','supplier','num_truck','employee','code_verefy','phonenumber','recive_pyement','discount','Reclaimed_products','previous_depts','remaining_amount','date','barcode','products']
    

############################# 


class ManualRecieptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualReceipt
        fields = '__all__'

    
class ManualRecieptProductsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    num_per_item = serializers.IntegerField(source='product.num_per_item')
    sale_price = serializers.FloatField(source='product.sale_price')
    
    class Meta :
        model = ManualReceipt_Products
        fields = ['id', 'name', 'num_per_item', 'sale_price', 'num_item', 'total_price', 'manualreceipt']


class ManualRecieptSerializer2(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name')
    products = ManualRecieptProductsSerializer(source='manualreceipt_products_set', many=True,read_only=True)
    class Meta:
        model = ManualReceipt
        fields = ['id','client_name','employee','verify_code','phonenumber','recive_payment','discount','reclaimed_products','previous_depts','remaining_amount','date','barcode','products']


########################################## OUTPUT ##############################################
        
class OutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Output
        fields = '__all__'
    


class ProductsOutputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='products.id')
    name = serializers.CharField(source='products.name')
    num_per_item = serializers.IntegerField(source='products.num_per_item')
    sale_price = serializers.FloatField(source='products.sale_price')

    class Meta:
        model = Output_Products
        fields = ['id', 'name', 'num_per_item', 'sale_price', 'quantity', 'total', 'discount', 'output']


class OutputSerializer2(serializers.ModelSerializer):
    products = ProductsOutputSerializer(source='output_products_set', many=True,read_only=True)
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = Output
        fields = ['id', 'client', 'employee', 'verify_code', 'phonenumber', 'recive_pyement', 'discount', 'Reclaimed_products', 'previous_depts', 'remaining_amount', 'date', 'barcode','longitude','latitude', 'products']

    def get_longitude(self, obj):
        return obj.location.x

    def get_latitude(self, obj):
        return obj.location.y


##########################################

class DelevaryArrivedSerializer(serializers.ModelSerializer):
    output_receipt = OutputSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = DelievaryArrived
        fields = '__all__'






        

###########################################################################################################
        












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
        reper['image'] = request.build_absolute_uri(instance.product.image.url)
        reper['sale_price'] = instance.product.sale_price
        reper['description'] = instance.product.description

        return reper