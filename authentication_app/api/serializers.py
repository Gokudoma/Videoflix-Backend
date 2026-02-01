from rest_framework import serializers
from ..models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates the email, password, and password confirmation.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Check that the two password entries match.
        """
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """
        Create a new user instance.
        
        The user is created as inactive by default and must be activated via email.
        """
        # Remove confirmed_password as it is not a model field
        validated_data.pop('confirmed_password')
        
        user = CustomUser.objects.create_user(
            username=validated_data['email'], # Username is required by Django, we set it to email
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_active = False  # Deactivate account until email verification
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for the login request.
    Validates that email and password are provided.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for the password reset request.
    Validates that an email is provided.
    """
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password.
    Validates that the two password fields match.
    """
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Check that the two password entries match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password": "Passwords must match."})
        return data