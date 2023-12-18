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
    return  name

# class signupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=CustomUser
#         fields = ['phonenumber','username', 'password']

#     def save(self, **kwargs):
#         user = CustomUser(
#             phonenumber=self.validated_data['phonenumber'],
#             username = self.validated_data['username']
#         )
#         password = self.validated_data['password']
#         user.set_password(password)
#         user.is_active = False
#         user.save()
    
#         return user


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




class Advance_on_SalarySerializer(serializers.ModelSerializer):
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
    



class BonusSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()

    class Meta:
        model = Bonus
        fields = '__all__'

    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        bonus = Bonus.objects.create(employee=employee, **validated_data)
        return bonus

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



class ExtraExpenseSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()
    class Meta:
        model = Extra_Expense
        fields = '__all__'
    
    def create(self, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        extra_expense = Extra_Expense.objects.create(employee=employee, **validated_data)
        return extra_expense
    
    def update(self, instance, validated_data):
        employee_name = validated_data.pop('employee')
        employee = Employee.objects.get(name=employee_name)
        instance.employee = validated_data.get('employee', employee)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.barcode = validated_data.get('barcode', instance.barcode)
        instance.save()
        return instance


    
class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = '__all__'



class Product2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'




class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod




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



class RegistrySerialzier(serializers.ModelSerializer):
    class Meta :
        model = Registry
        fields = ['total']


class Client_DebtSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    client_name = serializers.CharField()
    class Meta :
        model = Debt_Client
        fields = '__all__'

    def create(self, validated_data):
        client_ = validated_data.pop('client')
        client = Client.objects.get(name=client_)
        debt = Debt_Client.objects.create(client=client, **validated_data)
        return debt

    def update(self, instance, validated_data):
        client_ = validated_data.pop('client', None)
        if client_ is not None:
            client = Client.objects.get(name=client_)
            instance.client = client
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_total_expenses(self, obj):
        return Debt_Client.get_total_expenses()

    def get_total_amount(self, obj):
        return Debt_Client.get_total_amount()




class Supplier_DebtSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    supplier_name = serializers.CharField()
    class Meta :
        model = Debt_Supplier
        fields = '__all__'

    def create(self, validated_data):
        supplier_ = validated_data.pop('client')
        supplier = Client.objects.get(name=supplier_)
        debt = Debt_Supplier.objects.create(supplier_name=supplier, **validated_data)
        return debt

    def update(self, instance, validated_data):
        supplier_ = validated_data.pop('client', None)
        if supplier_ is not None:
            supplier = Supplier.objects.get(name=supplier_)
            instance.supplier_name = supplier
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_total_expenses(self, obj):
        return Debt_Supplier.get_total_expenses()

    def get_total_amount(self, obj):
        return Debt_Supplier.get_total_amount()






class DepositeSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    client = serializers.CharField()
    class Meta:
        model = Deposite
        fields = '__all__'

    def create(self, validated_data):
        client_name = validated_data.pop('client')
        client = Client.objects.get(name=client_name)
        deposite = Deposite.objects.create(client=client, **validated_data)
        return deposite

    def update(self, instance, validated_data):
        client_name = validated_data.pop('client', None)
        if client_name is not None:
            client = Client.objects.get(name=client_name)
            instance.client = client
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def get_total_expenses(self, obj):
        return Deposite.get_total_expenses()

    def get_total_amount(self, obj):
        return Deposite.get_total_amount()




class WithDrawSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    client = serializers.CharField()
    class Meta:
        model = WithDraw
        fields = '__all__'

    def create(self, validated_data):
        client_name = validated_data.pop('client')
        client = Client.objects.get(name=client_name)
        withdraw = WithDraw.objects.create(client=client, **validated_data)
        return withdraw
    
    def update(self, instance, validated_data):
        client_name = validated_data.pop('client', None)
        if client_name is not None:
            client = Client.objects.get(name=client_name)
            instance.client = client
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_total_expenses(self, obj):
        return WithDraw.get_total_expenses()

    def get_total_amount(self, obj):
        return WithDraw.get_total_amount()




