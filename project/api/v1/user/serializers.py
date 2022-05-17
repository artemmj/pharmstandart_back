from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from phonenumber_field.serializerfields import PhoneNumberField

from apps.user.models import User, PharmUser


class UserCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone')


class UserReadSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'phone', 'username', 'first_name', 'middle_name',
            'last_name', 'image', 'birthday', 'work_address', 'about',
            'skills', 'is_test_user',
        )


class UserLoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    is_test_user = serializers.BooleanField()


class UserChangePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    def validate_password1(self, value):
        validate_password(value)
        return value

    def validate_password2(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise ValidationError({
                'detail': 'Пароли не совпадают',
                'source': '',
                'status': 401,
            })
        return super().validate(attrs)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password1'])
        instance.save()
        return self.instance


class UserWriteSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(validators=[UniqueValidator(queryset=User.objects.all())], required=False)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password2 = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'phone', 'email', 'first_name', 'middle_name', 'last_name', 'username',
            'image', 'password', 'password2', 'birthday', 'work_address', 'about', 'skills',
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_password2(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):

        if 'password2' in attrs and 'password' in attrs:
            if attrs['password'] != attrs['password2']:
                raise ValidationError({
                    'detail': 'Пароли не совпадают',
                    'source': '',
                    'status': 401,
                })
        return super().validate(attrs)

    def create(self, validated_data):
        """ Регистрация пользователя """
        pass_ = validated_data.pop('password', None)
        if not pass_:
            raise ValidationError({
                'detail': 'В запросе отсутствует параметр с паролем',
                'source': 'password',
                'status': 400,
            })

        pass2 = validated_data.pop('password2', None)
        if not pass2:
            raise ValidationError({
                'detail': 'В запросе отсутствует параметр с подтверждением пароля',
                'source': 'password2',
                'status': 400,
            })

        user = User.objects.create(**validated_data)
        user.is_test_user = True
        user.set_password(pass2)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password2' in validated_data and 'password' in validated_data:
            validated_data.pop('password2')
            password = validated_data.pop('password')
            instance.set_password(password)
            instance.save()

        return super().update(instance, validated_data)


class VacationRowSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    class Meta:
        fields = ('count', 'start', 'end',)


class GetFactDaysVacationSerializer(serializers.Serializer):
    available_days = serializers.CharField()
    total = serializers.CharField()
    rows = serializers.ListField(child=VacationRowSerializer())

    class Meta:
        fields = ('available_days', 'total', 'rows',)


class GetPlanDaysVacationSerializer(serializers.Serializer):
    available_days = serializers.DateTimeField()
    total = serializers.CharField()
    rows = serializers.ListField(child=VacationRowSerializer())

    class Meta:
        fields = ('available_days', 'total', 'rows',)


class GetVacationScheduleSerializer(serializers.Serializer):
    s_error = serializers.BooleanField()
    s_message = serializers.CharField()
    fact = GetFactDaysVacationSerializer()
    plan = GetPlanDaysVacationSerializer()

    class Meta:
        fields = ('s_error', 's_message', 'fact', 'plan')


class GetVacationDaysCountSerializer(serializers.Serializer):
    s_error = serializers.BooleanField()
    s_message = serializers.CharField()
    s_time = serializers.CharField()
    Count = serializers.CharField()

    class Meta:
        fields = ('s_error', 's_message', 's_time', 'Count')


class PharmUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmUser
        fields = ('__all__')


class RequestsForDocumentsSerializer(serializers.Serializer):
    title = serializers.CharField()
    created_date = serializers.DateTimeField()
    modified_date = serializers.DateTimeField()
    type = serializers.CharField()
    status = serializers.CharField()
    department = serializers.CharField()
    author_comment = serializers.CharField()
    looked = serializers.CharField()
    author_name = serializers.CharField()
    author_login = serializers.CharField()
    editor_name = serializers.CharField()
    editor_login = serializers.CharField()
    attachments_count = serializers.CharField()


class RequestOrgTypesSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    order = serializers.CharField()


class SendRequestDocumentSerializer(serializers.Serializer):
    type_document = serializers.CharField(required=True)
    comment = serializers.CharField(required=True)
    files = serializers.ListField(child=serializers.FileField(), required=False)

    def validate_files(self, value):
        for file_obj in value:
            file_size = file_obj.size
            limit_kb = 15000
            if file_size > limit_kb * 1024:
                raise ValidationError({
                    'detail': f'Максимальный размер файла не должен быть больше {limit_kb / 1000} МБ!',
                    'source': '',
                    'status': 401,
                })


class SendRequestDocsFilesSerializer(serializers.Serializer):
    Length = serializers.CharField()
    Name = serializers.CharField()


class SendRequestDocumentSerializerResult(serializers.Serializer):
    s_error = serializers.BooleanField()
    s_message = serializers.CharField()
    s_time = serializers.DateTimeField()
    ItemId = serializers.IntegerField()
    Files = serializers.ListField(child=SendRequestDocsFilesSerializer())


class DatesForPaySheetSerializer(serializers.Serializer):
    month = serializers.DateField()


class SendPaySheetRequestSerializer(serializers.Serializer):
    month = serializers.DateField()


class GetUflexBase64Serializer(serializers.Serializer):
    base64data = serializers.CharField()
