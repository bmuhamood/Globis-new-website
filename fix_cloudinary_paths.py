import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globis_project.settings')
django.setup()

from main.models import Client  # Adjust to your model

# Update all client logo paths
for client in Client.objects.all():
    if client.logo and '/media/' in client.logo.name:
        # Remove /media/ prefix
        new_path = client.logo.name.replace('/media/', '').replace('media/', '')
        client.logo.name = new_path
        client.save()
        print(f"Updated {client.name}: {new_path}")

print("✅ All paths updated!")
