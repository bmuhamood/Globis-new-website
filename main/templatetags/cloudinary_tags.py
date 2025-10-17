from django import template
import re

register = template.Library()

@register.filter
def cloudinary_url(image_path):
    """Convert local image path to Cloudinary URL"""
    if not image_path:
        return ''
    
    # Convert to string
    path = str(image_path)
    
    # Remove /media/ prefix
    path = re.sub(r'^/?media/', '', path)
    
    # Remove file extension for Cloudinary
    path = re.sub(r'\.(png|jpg|jpeg|PNG|JPG|JPEG)$', '', path)
    
    # Build Cloudinary URL
    cloud_name = 'drcy2xxkg'
    return f'https://res.cloudinary.com/{cloud_name}/image/upload/{path}.png'