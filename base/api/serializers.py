from rest_framework import serializers
from base.models import *
from django.contrib.auth import login , authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.serializers import StringRelatedField
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

def modify_name(name):
    return name

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phonenumber','username', 'password']

    def validate(self, data):
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['phonenumber','username', 'password']

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
            username = self.validated_data['username']
        )
        password = self.validated_data['password']
        user.set_password(password)
        # user.is_active = False
        user.save()
        return user




class UserLoginSerilizer(serializers.ModelSerializer):

    phonenumber = serializers.CharField()
    password = serializers.CharField(max_length=55, min_length=6,write_only = True)

    class Meta:
        model = CustomUser
        fields = ['phonenumber', 'password']

    def validate(self, data):

        phonenumber = data.get('phonenumber', )
        password = data.get('password',)

        if phonenumber is None:
                raise serializers.ValidationError({'message_error':'An phonenubmer address is required to log in.'})
        
        if password is None:
            raise serializers.ValidationError({'message_error':'A password is required to log in.'})
        
        user = authenticate(username= phonenumber, password= password)

        if user is None:
            raise serializers.ValidationError({'message_error':'A user with this phonenumber and password was not found.'})
        
        if not user.is_active:
            raise serializers.ValidationError({'message_error':'This user is not currently activated.'})
        
        return data



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
        total = Point.objects.filter(Q(client=obj)&Q(is_used=False)).aggregate(total_points=models.Sum('number'))['total_points'] or 0
        return total


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVerification
        fields = '__all__'



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id','name','company_name','address','phone_number','info']
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id','customer','items','get_items_num','total_cart_price']


class Cart_ProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer()
    class Meta:
        model = Cart_Products
        fields = ['id','quantity','cart','products','total_price_of_item']




class ResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(style={"input_type":"password"}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ['password', 'new_password']
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






class UserLoginSerilizer(serializers.ModelSerializer):
    phonenumber = serializers.CharField()
    password = serializers.CharField(max_length=55, min_length=6,write_only = True)

    class Meta:
        model = CustomUser
        fields = ['phonenumber', 'password']

    def validate(self, data):
        phonenumber = data.get('phonenumber', )
        password = data.get('password',)
        if phonenumber is None:
                raise serializers.ValidationError({'message_error':'An phonenubmer address is required to log in.'})
        
        if password is None:
            raise serializers.ValidationError({'message_error':'A password is required to log in.'})
        
        user = authenticate(username= phonenumber, password= password)

        if user is None:
            raise serializers.ValidationError({'message_error':'A user with this phonenumber and password was not found.'})
        
        if not user.is_active:
            raise serializers.ValidationError({'message_error':'This user is not currently activated.'})
        
        return data
    

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



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


    
class IncomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming
        fields = '__all__'


class IncomingProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming_Products
        fields = '__all__'


################################# HR ##################################################################

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



class SalarySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=False)
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

class Product2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ManualRecieptSerializer(serializers.ModelSerializer):
    # products = serializers.ListField(child=serializers.CharField(), write_only=True)
    # products_name = ProductSerializer(source='products', many=True, read_only=True)
    employee = serializers.CharField()
    client = serializers.CharField()

    class Meta:
        model = ManualReciept
        fields = '__all__'

    def create(self, validated_data):
        emplyee_name= validated_data.pop('employee')
        employee = Employee.objects.filter(name=emplyee_name).first()
        client_name = validated_data.pop('client')
        client = Client.objects.filter(name=client_name).first()
        manual_reciept = ManualReciept.objects.create(
            employee=employee,
            client = client,
            **validated_data
        )
        manual_reciept.save()
        return manual_reciept
    


class ManualRecieptProductsSerializer(serializers.ModelSerializer):
    # products_name = ProductSerializer(source='products', many=True, read_only=True)
    # manual_name = ManualRecieptSerializer(read_only=True)
    class Meta :
        model = ManualReciept_Products
        fields = '__all__'

################################### Registry ##############################################################

class RegistrySerialzier(serializers.ModelSerializer):
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



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class RecievedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recieved_Payment
        fields = '__all__'

#######################################################################################################3###

class OutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputs
        fields = '__all__'
    
class ProductsOutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputs_Products
        fields = '__all__'


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = '__all__'

class ProductsMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium_Products
        fields = '__all__'




class ReturnedGoodsClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedGoodsClient
        fields = '__all__'


class ReturnedGoodsSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedGoodsSupplier
        fields = '__all__'






# --------------------------------------CREATE MEDIUM--------------------------------------
# class MediumSerializer(serializers.ModelSerializer):
#     class Meta:
#         models = Medium
#         fields = '__all__'

# class ProductsMediumSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Products_Medium
#         fields = '__all__'


# ------------------------------------------RETURNED GOODS------------------------------------------
    
class ReturnedGoodsSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedGoodsSupplier
        fields = '__all__'

class ReturnedGoodsClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedGoodsClient
        fields = '__all__'

# # ------------------------------------------DAMAGED PRODUCTS------------------------------------------

class DamagedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamagedProduct
        fields  ='__all__'

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