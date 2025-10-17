from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()
print("Your SECRET_KEY:")
print(secret_key)
print("\nCopy this and add it to your Render environment variables")