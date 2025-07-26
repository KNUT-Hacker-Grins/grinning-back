from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import re

User = get_user_model()

class LoginRequestSerializer(serializers.Serializer):
    """소셜 로그인 요청용 시리얼라이저"""

    provider = serializers.ChoiceField(choices=['kakao', 'google'])
    code = serializers.CharField(max_length=500)

    def validate_provider(self, value):
        """제공자 검증"""
        if value not in ['kakao', 'google']:
            raise serializers.ValidationError("지원하지 않는 소셜 로그인 제공자입니다.")
        return value

    def validate_code(self, value):
        """인증 코드 검증"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("인증 코드가 필요합니다.")
        return value


class RegisterRequestSerializer(serializers.ModelSerializer):
    """이메일/비밀번호 기반 회원가입 요청용 시리얼라이저"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'phone_number': {'required': False},
        }

    def validate_phone_number(self, value):
        """전화번호 유효성 검사: 010으로 시작하고 뒤에 8자리 숫자"""
        if value: # 전화번호가 입력된 경우에만 검사
            # 정규 표현식: ^010\d{8}$ (010으로 시작하고 정확히 8개의 숫자가 뒤따름)
            if not re.fullmatch(r'^010\d{8}'
, value):
                raise serializers.ValidationError("전화번호는 '010'으로 시작하고 뒤에 8자리 숫자가 와야 합니다. (예: 01012345678)")
            # 전화번호 중복 검사 (선택 사항이지만, unique=True 설정했으므로 필요)
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("이미 등록된 전화번호입니다.")
        return value

    def validate(self, data):
        """비밀번호와 비밀번호 확인이 일치하는지 검증 및 비밀번호 보안 조건 검사"""
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})

        # 비밀번호 보안 조건 검사
        if len(password) < 8:
            raise serializers.ValidationError({"password": "비밀번호는 최소 8자 이상이어야 합니다."})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "비밀번호는 최소 하나의 대문자를 포함해야 합니다."})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "비밀번호는 최소 하나의 소문자를 포함해야 합니다."})
        if not re.search(r'\d', password):
            raise serializers.ValidationError({"password": "비밀번호는 최소 하나의 숫자를 포함해야 합니다."})
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>/?]', password):
            raise serializers.ValidationError({"password": "비밀번호는 최소 하나의 특수문자(!@#$%^&*()_+-=[]{}|;:',.<>/? 등)를 포함해야 합니다."})

        return data

    def create(self, validated_data):
        """새로운 사용자 생성"""
        validated_data.pop('password_confirm')

        user = User.objects.create_user(  # type: ignore
            social_id=validated_data['email'],
            email=validated_data['email'],
            name=validated_data['name'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            provider='email'
        )
        return user


class LoginPasswordRequestSerializer(serializers.Serializer):
    """이메일/비밀번호 기반 로그인 요청용 시리얼라이저"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

            # 비밀번호 검증
            if not user.check_password(password):
                raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

            # 소셜 로그인으로 가입된 사용자는 이메일/비밀번호 로그인 불가
            if user.provider != 'email':  #type: ignore
                raise serializers.ValidationError("소셜 로그인으로 가입된 계정입니다. 소셜 로그인을 이용해주세요.")

            data['user'] = user # 유효한 사용자 객체를 데이터에 추가
        else:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """사용자 프로필 수정 요청용 시리얼라이저"""
    class Meta:
        model = User
        fields = ['name', 'phone_number']
        extra_kwargs = {
            'name': {'required': False},
            'phone_number': {'required': False},
        }

    def validate_phone_number(self, value):
        """전화번호 유효성 검사: 010으로 시작하고 뒤에 8자리 숫자"""
        if value: # 전화번호가 입력된 경우에만 검사
            if not re.fullmatch(r'^010\d{8}'
, value):
                raise serializers.ValidationError("전화번호는 '010'으로 시작하고 뒤에 8자리 숫자가 와야 합니다. (예: 01012345678)")
            # 전화번호 중복 검사 (자신을 제외한 다른 사용자와 중복되는지 확인)
            if self.instance and User.objects.exclude(id=self.instance.id).filter(phone_number=value).exists():
                raise serializers.ValidationError("이미 다른 사용자가 등록한 전화번호입니다.")
            elif not self.instance and User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("이미 등록된 전화번호입니다.")
        return value
