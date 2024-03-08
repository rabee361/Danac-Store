from rest_framework import serializers
from base.models import *
from django.contrib.auth import  authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from django.db.models import Q , Sum , F
from deep_translator import GoogleTranslator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.validators import ValidationError

############################################################## AUTHENTICATION ###################################################


############## Helper Functions ################
def translate_to_arabic(text):
    translator = GoogleTranslator(source='auto', target='ar')
    return translator.translate(text)

def modify_name(name):
    return name

class DateOnlyField(serializers.DateTimeField):
    def to_representation(self, value):
        return value.date()

#################################################



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'phonenumber', 'address','password', 'image']


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
    # phonenumber = serializers.CharField(read_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError("Incorrect Credentials")
            if not user.is_active:
                raise serializers.ValidationError({'message_error':'this account is not active'})
            if not user.is_accepted:
                raise serializers.ValidationError({'message_error':'this account is not accepted'})
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data



class SignUpSerializer(serializers.ModelSerializer):
    x = serializers.FloatField(write_only=True)
    y = serializers.FloatField(write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['phonenumber', 'username', 'password','password2','x','y','store_name','work_hours' ,'state','town','address']
        extra_kwargs = {
            'password':{'write_only':True,}
        }
    def validate(self, validated_data):
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({"password": "Passwords doesn't match."})

        validate_password(validated_data['password'])
        return validated_data

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def save(self, **kwargs):
        x = self.validated_data['x']
        y = self.validated_data['y']
        user = CustomUser(
            phonenumber=self.validated_data['phonenumber'],
            username = self.validated_data['username'],
            work_hours = self.validated_data['work_hours'],
            store_name = self.validated_data['store_name'],
            state = self.validated_data['state'],
            town = self.validated_data['town'],
            address = self.validated_data['address'],
            location = Point(x,y)
        )
        password = self.validated_data['password']

        user.set_password(password)
        user.is_active = False
        user.save()
        return user




class SerializerNotification(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
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



class ResetPasswordSerializer(serializers.Serializer):
    newpassword = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password', '')
        newpassword = attrs.get('newpassword', '')
        validate_password(password)
        validate_password(newpassword)
        if password != newpassword:
            raise serializers.ValidationError({'message_error':'كلمات المرور لم تتطابق'})
        
        return attrs
    

    def save(self, **kwargs):
        user_id = self.context.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        password = self.validated_data['newpassword']
        user.set_password(password)
        user.is_verified=False
        user.save()
        return user


### delete
class CodeVerivecationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVerification
        fields = '__all__'



class StateSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    class Meta:
        model = State
        fields = ['id','name','longitude','latitude']

    def get_longitude(self, obj):
        return obj.location.x

    def get_latitude(self, obj):
        return obj.location.y


############################################################### PRODUCT AND CLIENTS AND ORDERS ###########################################





class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id','image','name','total_product_types']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','product_type','name','image','total_categories']


class ClientSerializer(serializers.ModelSerializer):
    phonenumber = serializers.CharField()
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id','name', 'address', 'phonenumber','phonenumber2', 'category', 'notes', 'longitude','latitude', 'total_points','debts','total_receipts']

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
    
    def get_longitude(self,obj):
        return obj.location.x
    
    def get_latitude(self,obj):
        return obj.location.y





class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    carton_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_carton_price(self,obj):
        return obj.item_per_carton * obj.sale_price 
        
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
                raise serializers.ValidationError({"category": "Object with this name does not exist."})
        return super(ProductSerializer, self).update(instance, validated_data)


    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['name'] = modify_name(repr['name'])
        repr['category'] = instance.category.name
        return repr



class Product2Serializer(serializers.ModelSerializer):
    category = serializers.CharField()
    image = serializers.SerializerMethodField()
    carton_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_carton_price(self,obj):
        return obj.item_per_carton * obj.sale_price 

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
        fields = ['id','name','points','item_per_carton','sale_price','image']

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)




class Cart_ProductsSerializer(serializers.ModelSerializer):
    products = Product3Serializer()
    class Meta:
        model = Cart_Products
        fields = ['id','quantity','cart','products','total_price_of_item']



class Client_DetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id','name','phonenumber','address']



class Cart_Product_DetailsSerialzier(serializers.ModelSerializer):
    total_points = serializers.IntegerField(source='cart.total_cart_points',read_only=True)
    total_price = serializers.FloatField(source='cart.total_cart_price',read_only=True)
    barcode = serializers.CharField(source='cart.barcode',read_only=True)
    item_per_carton = serializers.IntegerField(source='products.item_per_carton',read_only=True)
    sale_price = serializers.FloatField(source='products.sale_price',read_only=True)
    product_name = serializers.CharField(source='products.name',read_only=True)
    points = serializers.IntegerField(source='products.points',read_only=True)
    product_id = serializers.IntegerField(source='products.id',read_only=True)

    class Meta:
        model = Cart_Products
        fields = ['id','product_id','points','product_name','quantity','item_per_carton','sale_price','total_price_of_item','total_points_of_item','total_price','total_points','barcode']




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
    points = serializers.IntegerField(source='product.points',read_only=True)
    product_name = serializers.CharField(source='product.name',read_only=True)
    num_per_item = serializers.IntegerField(source='product.num_per_item',read_only=True)

    class Meta:
        model = Order_Product
        fields = ['product_name','order','quantity','price','num_per_item','total_price','image','description','points']



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
        fields = ['id','client_id','address','name','phonenumber','client_service','products','total_price','shipping_cost','total','total_points','products_num','created','longitude','latitude','barcode']

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






class AdSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True,many=False)
    class Meta:
        model = Ad
        fields = '__all__'




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
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        related_models = {
            'overtime':'overtime_set',
            'absence':'absence_set',
            'bonus':'bonus_set',
            'discount':'discount_set',
        }
        totals = {}
        for key,value in related_models.items():
            related_objects = getattr(instance, value).all()
            total = sum(obj.amount for obj in related_objects)
            totals[value] = total
            representation[key] = total
        return representation


        
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
        fields = ['id','name','company_name','address','phone_number','phone_number2','info','debts','total_receipts']

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




class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name']


class SalarySerializer(serializers.ModelSerializer):
    hr = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Salary
        fields = '__all__'
        read_only_fields = ('hr',)

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
        fields = ['employee','total']


class Client_DebtSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='client_name.id',read_only=True)

    class Meta :
        model = Debt_Client
        fields = ['id','client_name','client_id','amount','payment_method','bank_name','receipt_num','date','total_client_debts','total_sum','added_to_registry']

    def create(self, validated_data):
        debt_client = Debt_Client.objects.create(**validated_data)
        client = debt_client.client_name
        if client.debts >= debt_client.amount:
            client.debts -= debt_client.amount
            client.save()
        else:
            debt_client.delete()
            raise serializers.ValidationError({"error":"المبلغ المدخل أكبر من الدين الموجود"})
        return debt_client

    def update(self, instance, validated_data):
        debt_difference = instance.amount - validated_data.get('amount')
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
    supplier_id = serializers.IntegerField(source='supplier_name.id',read_only=True)
    class Meta :
        model = Debt_Supplier
        fields = ['id','supplier_name','supplier_id','amount','payment_method','bank_name','receipt_num','date','total_supplier_debts','total_sum','added_to_registry']

    def create(self, validated_data):
        debt_supplier = Debt_Supplier.objects.create(**validated_data)
        supplier = debt_supplier.supplier_name
        if supplier.debts >= debt_supplier.amount:
            supplier.debts -= debt_supplier.amount
            supplier.save()
        else:
            debt_supplier.delete()
            raise serializers.ValidationError({"error":"المبلغ المدخل أكبر من الدين الموجود"})
        return debt_supplier


    def update(self, instance, validated_data):
        debt_difference = instance.amount - validated_data.get('amount')
        instance = super().update(instance, validated_data)
        supplier = instance.supplier_name
        print(debt_difference)
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
    client_id = serializers.IntegerField(source='client.id',read_only=True)
    class Meta:
        model = Deposite
        fields = ['id','client','client_id','deposite_name','detail_deposite','total','registry','verify_code','total_deposites','total_sum','date']

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
        request = self.context['request']
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        registry = Registry.objects.get(employee=employee)
        deposite = Deposite.objects.create(**validated_data)
        registry = Registry.objects.first()
        registry.total += deposite.total
        registry.save()
        return deposite

    def update(self, instance, validated_data):
        request = self.context['request']
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        registry = Registry.objects.get(employee=employee)
        if instance.registry != registry:
            raise serializers.ValidationError("you are not allowed into this registry!")
        
        difference = validated_data.get('total', instance.total) - instance.total
        super().update(instance, validated_data)
        registry.total += difference
        registry.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = instance.client.name
        return representation




class WithDrawSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source='client.id',read_only=True)

    class Meta:
        model = WithDraw
        fields = ['id','client','client_id','withdraw_name','details_withdraw','total','registry','verify_code','total_withdraws','total_sum','date']

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
        request = self.context['request']
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        registry = Registry.objects.get(employee=employee)
        validated_data['registry'] = registry
        withdraw = WithDraw.objects.create(**validated_data)
        registry.total -= withdraw.total
        registry.save()
        return withdraw

            
    def update(self, instance, validated_data):
        request = self.context['request']
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        registry = Registry.objects.get(employee=employee)
        validated_data['registry'] = registry
        if instance.registry != registry:
            raise serializers.ValidationError("you are not allowed into this registry!")
        
        difference = validated_data.get('total', instance.total) - instance.total
        super().update(instance, validated_data)
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
    class Meta:
        model = Expense
        fields = ['id','expense_name','details','name','amount','receipt_num','date','total_expenses','total_amount','added_to_registry']
    
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
    class Meta:
        model = Payment
        fields = ['id','employee','name','payment_method','bank_name','receipt_num','amount','date','total_payments','total_amount','added_to_registry']

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
        fields = ['id','employee','name','payment_method','bank_name','receipt_num','amount','date','total_recieved_payments','total_amount','added_to_registry']

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
    product_points = serializers.IntegerField(source='product.points',read_only=True)
    class Meta:
        model = Products_Medium
        fields = ['id','medium','product','product_id','price','num_item','total_price_of_item','product_points']
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
    product_id = serializers.IntegerField(source='product.id',read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    package_id = serializers.CharField(write_only=True)#####

    class Meta:
        model = ReturnedGoodsClient
        fields = ['id','product','product_id','quantity','total_price','reason','package_id']

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
        package_id = validated_data.pop('package_id')#####
        instance = super().create(validated_data)
        product = instance.product
        product.quantity -= instance.quantity
        product.save()
        package = ReturnedClientPackage.objects.get(id=package_id)####
        package.goods.add(instance)####
        package.save()#####
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        return representation




class ReturnedClientPackageSerializer(serializers.ModelSerializer):
    goods = ReturnedGoodsClientSerializer(many=True,read_only=True)
    class Meta:
        model = ReturnedClientPackage
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        employee = Employee.objects.filter(phonenumber=request.user.phonenumber).first()
        instance = ReturnedClientPackage.objects.create(employee,**validated_data)
        return instance


class ReturnedGoodsSupplierSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    package_id = serializers.CharField(write_only=True)
    class Meta:
        model = ReturnedGoodsSupplier
        fields = ['id', 'product', 'quantity', 'total_price', 'reason','package_id']

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
        package_id = validated_data.pop('package_id')#####
        instance = super().create(validated_data)
        product = instance.product
        product.quantity -= instance.quantity
        product.save()
        package = ReturnedSupplierPackage.objects.get(id=package_id)####
        package.goods.add(instance)####
        package.save()#####
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        return representation



###### new
class ReturnedSupplierPackageSerializer(serializers.ModelSerializer):
    goods = ReturnedGoodsSupplierSerializer(many=True,read_only=True)

    class Meta:
        model = ReturnedSupplierPackage
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)

    

    
############################################# DAMAGED PRODUCTS #########################################################

class DamagedProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    employee = serializers.CharField(read_only=True)
    package_id = serializers.CharField(write_only=True)#####

    class Meta:
        model = DamagedProduct
        fields  = ['id','product','quantity','employee','total_price','product_id','package_id']

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
        package_id = validated_data.pop('package_id')#####
        instance = super().create(validated_data)
        product = instance.product
        product.quantity -= instance.quantity
        product.save()
        package = DamagedPackage.objects.get(id=package_id)####
        package.goods.add(instance)####
        package.save()#####

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

    


class DamagedPackageSerializer(serializers.ModelSerializer):
    goods = DamagedProductSerializer(many=True,read_only=True)
    class Meta:
        model = DamagedPackage
        fields = ['id','date','total_num','total_price','barcode','goods']






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
        fields = ['id','serial','supplier','employee','total_receipt','supplier_phone','client_service','recive_pyement','discount','Reclaimed_products','previous_depts','remaining_amount','date','barcode','products','freeze']
    
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



class FrozenIncomingReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrozenIncomingReceipt
        fields = '__all__'



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
        fields = ['id','serial','client','client_phone','client_points','total_receipt','employee','client_service','discount','recive_payment','reclaimed_products','previous_depts','remaining_amount','date','barcode','products','freeze']

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




class FrozenManualReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrozenManualReceipt
        fields = '__all__'

########################################## OUTPUT ##############################################
        
class OutputSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name',read_only=True)
    address = serializers.CharField(source='client.address',read_only=True)
    class Meta:
        model = Output
        fields = ['id','serial','client','client_name','address','products','employee','phonenumber','recive_pyement','discount','Reclaimed_products','previous_depts','remaining_amount','date','barcode','location','delivered','freeze']


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
        barcode = Cart.objects.get(customer=client)
        instance = Output.objects.create(employee=employee, client=client,barcode=barcode, **validated_data)
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





class FrozenOutputReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrozenOutputReceipt
        fields = '__all__'


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
    





class ChatSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username',read_only=True)

    class Meta:
        model = Chat
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.user.image:
            return request.build_absolute_uri(obj.user.image.url)
        return None



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'