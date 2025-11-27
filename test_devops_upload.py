import requests
import os

# Config
BASE_URL = os.getenv('BELGRANO_AHORRO_URL', 'http://localhost:10000')
USERNAME = 'devops'
PASSWORD = 'DevOps2025!Secure'

def test_devops_upload():
    session = requests.Session()
    
    # 1. Login
    login_url = f"{BASE_URL}/devops/login"
    print(f"Logging in to {login_url}...")
    resp = session.post(login_url, data={'username': USERNAME, 'password': PASSWORD})
    if resp.url.endswith('/devops/login'):
        print("❌ Login failed")
        return
    print("✅ Login successful")

    # 2. Create Product with Image
    create_url = f"{BASE_URL}/devops/productos"
    
    # Create a dummy image file
    with open('test_image.jpg', 'wb') as f:
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xFF\xDA\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xFF\xD9')

    files = {
        'imagen': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')
    }
    data = {
        'nombre': 'Test DevOps Upload',
        'precio': '100',
        'categoria': 'Otros',
        'negocio': '1', # Assuming ID 1 exists or is handled gracefully
        'descripcion': 'Test upload from script'
    }

    print("Uploading product with image...")
    resp = session.post(create_url, data=data, files=files)
    
    if resp.status_code == 200:
        print("✅ Request successful")
        if "Test DevOps Upload" in resp.text:
             print("✅ Product found in response list")
        else:
             print("⚠️ Product not found in response list (might be on next page or failed silently)")
    else:
        print(f"❌ Request failed: {resp.status_code}")

    # Clean up
    os.remove('test_image.jpg')

if __name__ == "__main__":
    test_devops_upload()
