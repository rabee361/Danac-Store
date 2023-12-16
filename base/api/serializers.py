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
        fields = ['name','company_name','address','phone_number','info']
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class Cart_ProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer()
    class Meta:
        model = Cart_Products
        fields = fields = ['products', 'quantity']




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
    

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=serializers.CharField(), write_only=True)
    products_data = ProductSerializer(source='products', many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        product_names = validated_data.pop('products', [])
        order = Order.objects.create(**validated_data)

        for product_name in product_names:
            try:
                product = Product.objects.get(name=product_name)
                order.products.add(product)
            except Product.DoesNotExist:
                raise serializers.ValidationError({'error': f'Product with name {product_name} does not exist'})

        order.save()
        return order
    




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




class AdvanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advance_On_salary
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
    


class BonusSerializer(serializers.ModelSerializer):
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



class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra_Expense
        fields = '__all__'


    
class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = '__all__'



class Product2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
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