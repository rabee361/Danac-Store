from rest_framework import serializers
from base.models import *
from rest_framework.response import Response
from django.contrib.auth import  authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from django.db.models import Q , F , Sum
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python, PhoneNumber
from deep_translator import GoogleTranslator
def translate_to_arabic(text):
    translator = GoogleTranslator(source='auto', target='ar')
    return translator.translate(text)

############################################################## AUTHENTICATION ###################################################

def modify_name(name):
    return name

class DateOnlyField(serializers.DateTimeField):
    def to_representation(self, value):
        return value.date()

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
    phonenumber = serializers.CharField()
    class Meta:
        model = Client
        fields = ['id','name', 'address', 'phonenumber', 'category', 'notes', 'location', 'total_points','debts']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    
    def get_total_points(self,obj):
        total = Points.objects.filter(Q(client=obj)&Q(is_used=False)&Q(expire_date__gt=timezone.now())).aggregate(total_points=models.Sum('number'))['total_points'] or 0
        return total




class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    class Meta:
        model = Product
        fields = '__all__'
        
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
            
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
    price = serializers.FloatField(source='product.sale_price',read_only=True)
    description = serializers.CharField(source='product.description',read_only=True)

    class Meta:
        model = Order_Product
        fields = ['product','order','quantity','total_price','price','description']




class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    products = OrderProductsSerializer(source='order_product_set', many=True)
    class Meta:
        model = Order
        fields = ['id', 'client', 'products', 'total', 'products_num', 'created', 'delivery_date', 'delivered']





class OrderProductsSerializer2(serializers.ModelSerializer):
    image = serializers.ImageField(source='product.image')
    price = serializers.FloatField(source='product.sale_price',read_only=True)
    description = serializers.CharField(source='product.description')
    class Meta:
        model = Order_Product
        fields = ['product','order','quantity','price','total_price','image','description']



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


    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

        return not bool(self._errors)

        
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




class SalesEmployeeLocationSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        fields = ['longitude','latitude']

    def get_longitude(self, obj):
        return obj.location.x

    def get_latitude(self, obj):
        return obj.location.y


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id','name','company_name','address','phone_number','info','debts']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        return repr
    

############################################################## HR ##################################################################

class Advance_on_SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = Advance_On_salary
        fields = ['id','employee','employee_name','reason','amount','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    

class OverTimeSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = OverTime
        fields = ['id','employee','employee_name','num_hours','amount','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    

class AbsenceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = Absence
        fields = ['id','employee','employee_name','days','amount','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    

class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = Bonus
        fields = ['id','employee','employee_name','reason','amount','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
     

class DiscountSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = Discount
        fields = ['id','employee','employee_name','reason','amount','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    

class ExtraExpenseSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model = Extra_Expense
        fields = '__all__'
        fields = ['id','employee','employee_name','reason','amount','date','barcode']
        
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)




class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name']


class SalarySerializer(serializers.ModelSerializer):
    hr = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Salary
        fields = '__all__'
        read_only_fields = ('hr',)  # Add 'hr' to the read-only fields

    def create(self, validated_data):
        user = self.context['request'].user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        validated_data['hr'] = employee
        salary = Salary.objects.create(**validated_data)
        return salary

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['hr'] = instance.hr.name
        return repr



class EmployeeSalarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ['id','job_position','name','phonenumber' ,'salary','sale_percentage']

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

        sale_percentage = instance.sale_percentage if instance.sale_percentage is not None else 0


        total = instance.salary - totals['advance_on_salary_set'] - totals['extra_expense_set'] - totals['absence_set'] - totals['discount_set'] + totals['overtime_set'] + totals['bonus_set'] + (instance.salary * sale_percentage)
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
    client_id = serializers.IntegerField(source='client_name.id',read_only=True)
    class Meta :
        model = Debt_Client
        fields = ['id','client_name','client_id','amount','payment_method','bank_name','receipt_num','date','total_client_debts','total_sum']

    def get_total_client_debts(self, obj):
        return Debt_Client.get_total_client_debts()

    def get_total_sum(self, obj):
        return Debt_Client.get_total_sum()


    def create(self, validated_data):
        debt_client = validated_data['amount']
        client = debt_client.client_name
        if client.debts >= debt_client.amount:
            client.debts -= debt_client.amount
            client.save()
            debt_client = Debt_Client.objects.create(**validated_data)
        else:
            debt_client.delete()
            raise serializers.ValidationError({"error":"المبلغ المدخل أكبر من الدين الموجود"})
        return debt_client

    def update(self, instance, validated_data):
        debt_difference = validated_data.get('amount', instance.amount) - instance.amount
        instance = super().update(instance, validated_data)
        client = instance.client_name
        client.debts += debt_difference
        client.save()
        return instance

    
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client_name'] = instance.client_name.name
        return representation



class Supplier_DebtSerializer(serializers.ModelSerializer):
    total_supplier_debts = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    supplier_id = serializers.IntegerField(source='supplier_name.id',read_only=True)
    class Meta :
        model = Debt_Supplier
        fields = ['id','supplier_name','supplier_id','amount','payment_method','bank_name','check_num','date','total_supplier_debts','total_sum']

    def get_total_supplier_debts(self, obj):
        return Debt_Supplier.get_total_supplier_debts()

    def get_total_sum(self, obj):
        return Debt_Supplier.get_total_sum()
    
    def create(self, validated_data):
        supplier_debt = Debt_Supplier.objects.create(**validated_data)
        supplier = supplier_debt.supplier_name
        supplier.debts -= supplier_debt.amount
        supplier.save()
        return supplier_debt

    def update(self, instance, validated_data):
        debt_difference = validated_data.get('amount', instance.amount) - instance.amount
        instance = super().update(instance, validated_data)
        supplier = instance.supplier_name
        supplier.debts += debt_difference
        supplier.save()
        return instance

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['supplier_name'] = instance.supplier_name.name
        return representation



class DepositeSerializer(serializers.ModelSerializer):
    total_deposites = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    client_id = serializers.IntegerField(source='client.id',read_only=True)
    class Meta:
        model = Deposite
        fields = ['id','client','client_id','deposite_name','detail_deposite','total','verify_code','total_deposites','total_sum','date']

    def get_total_deposites(self, obj):
        return Deposite.get_total_deposites()

    def get_total_sum(self, obj):
        return Deposite.get_total_sum()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

    def create(self, validated_data):
        deposite = Deposite.objects.create(**validated_data)
        registry = Registry.objects.first()
        registry.total += deposite.total
        registry.save()
        return deposite

    def update(self, instance, validated_data):
        difference = validated_data.get('total', instance.total) - instance.total
        super().update(instance, validated_data)
        registry = Registry.objects.first()
        registry.total += difference
        registry.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = instance.client.name
        return representation




class WithDrawSerializer(serializers.ModelSerializer):
    total_withdraws = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    client_id = serializers.IntegerField(source='client.id',read_only=True)
    class Meta:
        model = WithDraw
        fields = ['id','client','client_id','withdraw_name','details_withdraw','total','verify_code','total_withdraws','total_sum','date']

    def get_total_withdraws(self, obj):
        return WithDraw.get_total_withdraws()

    def get_total_sum(self, obj):
        return WithDraw.get_total_sum()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

    def create(self, validated_data):
        withdraw = WithDraw.objects.create(**validated_data)
        registry = Registry.objects.first()
        registry.total -= withdraw.total
        registry.save()
        return withdraw

    def update(self, instance, validated_data):
        difference = validated_data.get('total', instance.total) - instance.total
        super().update(instance, validated_data)
        registry = Registry.objects.first()
        if registry.total - difference < 0:
            raise serializers.ValidationError("The total in the registry cannot go below zero.")
        registry.total -= difference
        registry.save()

        return instance
   
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = instance.client.name
        return representation



class ExpenseSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model = Expense
        fields = '__all__'

    def get_total_expenses(self, obj):
        return Expense.get_total_expenses()

    def get_total_amount(self, obj):
        return Expense.get_total_amount()
    
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)  


class PaymentSerializer(serializers.ModelSerializer):
    total_payments = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields = '__all__'

    def get_total_payments(self, obj):
        return Payment.get_total_payments()

    def get_total_amount(self, obj):
        return Payment.get_total_amount()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    


class RecievedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recieved_Payment
        fields = '__all__'

    def get_total_recieved_payments(self, obj):
        return Recieved_Payment.get_total_revieved_payments()

    def get_total_amount(self, obj):
        return Recieved_Payment.get_total_amount()

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
      
#################################################### Medium #######################################################################3###


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = '__all__'

class ProductsMediumSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False,read_only=True)
    product_id = serializers.IntegerField(source='product.id',read_only=True)
    class Meta:
        model = Products_Medium
        fields = ['id','medium','product','product_id','price','num_item','total_price_of_item']
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['num_per_item'] = instance.product.num_per_item
        repr['product'] = instance.product.name
        return repr


class UpdateProductMediumSerializer(serializers.ModelSerializer):
    medium = serializers.CharField()
    product = serializers.CharField()
    class Meta:
        model = Products_Medium
        fields = ['id','medium','product','price','num_item','total_price_of_item']

    def update(self, instance, validated_data):
        medium_id = validated_data.pop('medium')
        medium = Medium.objects.get(id=medium_id)
        product_id = validated_data.pop('product')
        product = Product.objects.get(id=product_id)
        instance.product = product
        instance.medium = medium
        instance.price = validated_data.get('price', instance.price)
        instance.num_item = validated_data.get('num_item', instance.num_item)
        instance.total_price = instance.price * instance.num_item
        instance.save()

        return instance

######################################## RETURNED GOODS #####################################################################




class ReturnedGoodsClientSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='client.id',read_only=True)
    product_id = serializers.IntegerField(source='product.id',read_only=True)
    employee_id = serializers.IntegerField(source='employee.id',read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = ReturnedGoodsClient
        fields = ['id','client','client_id','product','product_id','employee','employee_id','quantity','total_price','reason','date']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

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

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

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
        representation['supplier'] = instance.supplier.name
        representation['employee'] = instance.employee.name
        return representation

    
############################################# DAMAGED PRODUCTS #########################################################

class DamagedProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = DamagedProduct
        fields  = ['id','product','quantity','total_price','date','product_id']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)

    def create(self, validated_data):
        instance = super().create(validated_data)
        product = instance.product
        product.quantity -= instance.quantity
        product.save()

        return instance

    def update(self, instance, validated_data):
        original_quantity = instance.quantity
        super().update(instance, validated_data)
        quantity_diff = instance.quantity - original_quantity
        product = instance.product
        product.quantity -= quantity_diff
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



class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','num_per_item','sale_price']


class IncomingProductsSerializer2(serializers.ModelSerializer):
    # product = serializers.IntegerField(source='product.id',read_only=True)
    name = serializers.CharField(source='product.name',read_only=True)
    num_per_item = serializers.IntegerField(source='product.num_per_item',read_only=True)
    sale_price = serializers.FloatField(source='product.sale_price',read_only=True)

    class Meta:
        model = Incoming_Product
        fields = ['id', 'product','name', 'num_per_item', 'sale_price', 'num_item', 'total_price', 'incoming']

    def create(self, validated_data):
        product = validated_data.get('product')
        num_item = validated_data.get('num_item')
        incoming_receipt = validated_data.get('incoming')
        incoming_product = Incoming_Product.objects.filter(product=product,incoming=incoming_receipt).first()
        if incoming_product:
            incoming_product.num_item += num_item
            incoming_product.save()
            return incoming_product
        else:
            instance = super().create(validated_data)
            product.quantity -= num_item
            product.save()
            return instance

    def update(self, instance, validated_data):
        original_quantity = instance.num_item
        super().update(instance, validated_data)
        quantity_diff = instance.num_item - original_quantity
        product = instance.product
        product.quantity -= quantity_diff
        product.save()
        return instance
    
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)



class IncomingProductsSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    num_per_item = serializers.IntegerField(source='product.num_per_item')
    sale_price = serializers.FloatField(source='product.sale_price')

    class Meta:
        model = Incoming_Product
        fields = ['id', 'product_id','name', 'num_per_item', 'sale_price', 'num_item', 'total_price', 'incoming']



class IncomingSerializer2(serializers.ModelSerializer):
    products = IncomingProductsSerializer(source='incoming_product_set', many=True,read_only=True)
    supplier_phone = serializers.CharField(source='supplier.phone_number',read_only=True)
    total_receipt = serializers.SerializerMethodField()
    class Meta:
        model = Incoming
        fields = ['id','supplier','employee','total_receipt','supplier_phone','phonenumber','recive_pyement','discount','Reclaimed_products','previous_depts','remaining_amount','date','barcode','products']
    
    def get_total_receipt(self, obj):
        return obj.calculate_total_receipt()
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if self.context.get('show_datetime', False):
            repr['date'] = instance.date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            repr['date'] = instance.date.strftime("%Y-%m-%d")
        repr['supplier'] = instance.supplier.name
        repr['employee'] = instance.employee.name
        return repr



class IncomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incoming
        exclude = ['employee']
        

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)


    def create(self, validated_data):
        request = self.context.get('request')
        supplier_data = validated_data.pop('supplier', None)
        remaining_amount = validated_data.pop('remaining_amount', None)
        employee = Employee.objects.filter(phonenumber=request.user.phonenumber).first()
        supplier = Supplier.objects.get(id=supplier_data.id)
        instance = Incoming.objects.create(employee=employee, supplier=supplier,remaining_amount=remaining_amount ,**validated_data)
        supplier.debts += remaining_amount
        supplier.save()
        return instance
    
    def update(self, instance, validated_data):
        supplier_name = validated_data.pop('supplier', None)
        supplier = Supplier.objects.get(id=supplier_name.id)
        orginal_remaining_amount = instance.remaining_amount
        super().update(instance, validated_data)
        deff_remaining_amount = instance.remaining_amount - orginal_remaining_amount
        instance.supplier = supplier
        supplier.debts -= deff_remaining_amount
        supplier.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['supplier'] = instance.supplier.name
        return repr
     
    

############################# 




class ManualRecieptProductsSerializer2(serializers.ModelSerializer):
    # product = serializers.IntegerField()
    name = serializers.CharField(source='product.name',read_only=True)
    num_per_item = serializers.IntegerField(source='product.num_per_item',read_only=True)
    sale_price = serializers.FloatField(source='price')
    
    class Meta :
        model = ManualReceipt_Products
        fields = ['id', 'product','name', 'num_per_item', 'sale_price', 'num_item' ,'total_price', 'manualreceipt']

    def create(self, validated_data):
        product = validated_data.get('product')
        num_item = validated_data.get('num_item')
        manual_receipt = validated_data.get('manualreceipt')
        manual_product = ManualReceipt_Products.objects.filter(product=product,manualreceipt=manual_receipt).first()
        if manual_product:
            manual_product.num_item += num_item
            manual_product.save()
            return manual_product
        else:
            instance = super().create(validated_data)
            product.quantity -= num_item
            product.save()
            return instance

    def update(self, instance, validated_data):
        original_quantity = instance.num_item
        super().update(instance, validated_data)
        quantity_diff = instance.num_item - original_quantity
        product = instance.product
        product.quantity -= quantity_diff
        product.save()
        return instance
    
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)




class ManualRecieptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualReceipt
        exclude = ['employee']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    
    def create(self, validated_data):
        request = self.context.get('request')
        client_data = validated_data.pop('client', None)
        remaining_amount = validated_data.pop('remaining_amount', None)
        employee = Employee.objects.filter(phonenumber=request.user.phonenumber).first()
        client = Client.objects.get(id=client_data.id)
        instance = ManualReceipt.objects.create(employee=employee, client=client, **validated_data)
        client.debts += remaining_amount
        client.save()
        return instance

    def update(self, instance, validated_data):
        client_name = validated_data.pop('client', None)
        client = Client.objects.get(id=client_name.id)
        orginal_remaining_amount = instance.remaining_amount
        super().update(instance, validated_data)
        deff_remaining_amount = instance.remaining_amount - orginal_remaining_amount
        instance.client = client
        client.debts -= deff_remaining_amount
        client.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance  


class ManualRecieptProductsSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    num_per_item = serializers.IntegerField(source='product.num_per_item')
    sale_price = serializers.FloatField(source='price')
    
    class Meta :
        model = ManualReceipt_Products
        fields = ['id','product_id', 'name', 'num_per_item', 'sale_price', 'num_item','total_price', 'manualreceipt']


class ManualRecieptSerializer2(serializers.ModelSerializer):
    products = ManualRecieptProductsSerializer(source='manualreceipt_products_set', many=True,read_only=True)
    client_phone = serializers.CharField(source='client.phonenumber',read_only=True)
    total_receipt = serializers.SerializerMethodField()
    client_points = serializers.SerializerMethodField()
    class Meta:
        model = ManualReceipt
        fields = ['id','client','client_phone','client_points','total_receipt','employee','phonenumber','discount','recive_payment','reclaimed_products','previous_depts','remaining_amount','date','barcode','products']

    def get_total_receipt(self, obj):
        return obj.calculate_total_receipt()
    
    def get_client_points(self,obj):
        client = obj.client
        points = Points.objects.filter(client=client).aggregate(
            total = Sum('number')
        )['total'] or 0
        return points

        

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if self.context.get('show_datetime', False):
            repr['date'] = instance.date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            repr['date'] = instance.date.strftime("%Y-%m-%d")
        repr['employee'] = instance.employee.name
        repr['client'] = instance.client.name
        return repr

########################################## OUTPUT ##############################################
        
class OutputSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name',read_only=True)
    address = serializers.CharField(source='client.address',read_only=True)
    class Meta:
        model = Output
        fields = ['id','client','client_name','address','products','employee','phonenumber','recive_pyement','discount','Reclaimed_products','previous_depts','remaining_amount','date','barcode','location','delivered']


class ProductsOutputSerializer2(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name',read_only=True)
    num_per_item = serializers.IntegerField(source='product.num_per_item',read_only=True)
    sale_price = serializers.FloatField(source='product.sale_price',read_only=True)
    # total_price = serializers.FloatField(source='total',read_only=True)

    class Meta:
        model = Output_Products
        fields = ['id', 'product','name', 'num_per_item', 'sale_price', 'quantity', 'total_price', 'discount', 'output']

    def create(self, validated_data):
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        output_receipt = validated_data.get('output')
        output_product = Output_Products.objects.filter(product=product,output=output_receipt).first()
        if output_product:
            output_product.quantity += quantity
            output_product.save()
            return output_product
        else:
            instance = super().create(validated_data)
            product.quantity -= quantity
            product.save()
            return instance
        
    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    

    def update(self, instance, validated_data):
        original_quantity = instance.quantity
        super().update(instance, validated_data)
        quantity_diff = instance.quantity - original_quantity
        product = instance.product
        product.quantity -= quantity_diff
        product.save()
        return instance



class ProductsOutputSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    num_per_item = serializers.IntegerField(source='product.num_per_item')
    sale_price = serializers.FloatField(source='product.sale_price')
    num_item = serializers.IntegerField(source='quantity',read_only=True)
    # total_price = serializers.FloatField(source='total',read_only=True)

    class Meta:
        model = Output_Products
        fields = ['id', 'product_id','name', 'num_per_item', 'sale_price', 'num_item', 'total_price', 'discount', 'output']


class OutputSerializer2(serializers.ModelSerializer):
    products = ProductsOutputSerializer(source='output_products_set', many=True,read_only=True)
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    client_phone = serializers.CharField(source='client.phonenumber',read_only=True)
    total_receipt = serializers.SerializerMethodField()
    client_points = serializers.SerializerMethodField()

    class Meta:
        model = Output
        exclude = ['employee','location']
        include = ['total_receipt']

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if self._errors:
            first_error_field = next(iter(self._errors))
            first_error_message = self._errors[first_error_field][0]
            if first_error_message == "This field is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} مطلوب"
            elif first_error_message == "This field may not be blank.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "A valid number is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"رقم صالح مطلوب لـ {translation}"
            elif first_error_message == "A valid integer is required.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"عدد صحيح صالح مطلوب لـ {translation}"
            elif first_error_message == "This field may not be null.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"{translation} لا يمكن أن يكون فارغًا"
            elif first_error_message == "Invalid pk \"0\" - object does not exist.":
                translation = translate_to_arabic(first_error_field.replace('_', ' '))
                first_error_message = f"يرجى اختيار قيمة لـ {translation}"
            self._errors = {"error": first_error_message}
            if raise_exception:
                raise serializers.ValidationError(self._errors)
        return not bool(self._errors)
    
    def get_longitude(self, obj):
        return obj.location.x

    def get_latitude(self, obj):
        return obj.location.y

    def get_total_receipt(self, obj):
        return obj.calculate_total_receipt()
    
    def get_client_points(self,obj):
        client = obj.client
        points = Points.objects.filter(client=client).aggregate(
            total = Sum('number')
        )['total'] or 0
        return points

    def create(self, validated_data):
        request = self.context.get('request')
        client_data = validated_data.pop('client', None)
        remaining_amount = validated_data.pop('remaining_amount', None)
        employee = Employee.objects.filter(phonenumber=request.user.phonenumber).first()
        client = Client.objects.get(id=client_data.id)
        instance = Output.objects.create(employee=employee, client=client, **validated_data)
        client.debts += remaining_amount
        client.save()
        return instance
    
    def update(self, instance, validated_data):
        client_name = validated_data.pop('client', None)
        client = Client.objects.get(id=client_name.id)
        orginal_remaining_amount = instance.remaining_amount
        super().update(instance, validated_data)
        deff_remaining_amount = instance.remaining_amount - orginal_remaining_amount
        instance.client = client
        client.debts -= deff_remaining_amount
        client.save()        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance 

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if self.context.get('show_datetime', False):
            repr['date'] = instance.date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            repr['date'] = instance.date.strftime("%Y-%m-%d")
        repr['client'] = instance.client.name
        repr['employee'] = instance.employee.name
        return repr

##########################################

class DelevaryArrivedSerializer(serializers.ModelSerializer):
    output_receipt = OutputSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = DelievaryArrived
        fields = '__all__'


class GetProductsOutputsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='product.image',read_only=True)
    class Meta:
        model = Output_Products
        fields = ['product', 'quantity', 'total', 'discount','image']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['num_per_item '] = instance.product.num_per_item
        repr['sale_price'] = instance.product.sale_price
        repr['product'] = instance.product.name
        repr['image'] = self.context['request'].build_absolute_uri(instance.product.image.url)
        return repr



        

###########################################################################################################
        












# ---------------------------------------------ORDER ENVOY---------------------------------------------

class OrderEnvoySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderEnvoy
        fields = '__all__'
    # def to_representation(self, instance):
    #     print(instance.client.address)  # Add this line
    #     representation = super().to_representation(instance)
    #     return representation


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