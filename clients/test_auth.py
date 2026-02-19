import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def register(username, password):
    """Register a new user"""
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        print(f"Register response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Registration error: {e}")
        return None

def login(username, password):
    """Login and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        print(f"Login response: {data}")
        return data.get("token")
    except Exception as e:
        print(f"Login error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("CHAT APP - USER AUTHENTICATION TEST")
    print("=" * 50)
    
    # Test with a sample user
    username = input("\nEnter username (or press Enter for 'alice'): ").strip()
    if not username:
        username = "alice"
    
    password = input("Enter password (or press Enter for 'password123'): ").strip()
    if not password:
        password = "password123"
    
    print(f"\nUsing username: {username}")
    print(f"Using password: {password}")
    
    print("\n" + "=" * 50)
    print("STEP 1: REGISTRATION")
    print("=" * 50)
    register(username, password)
    
    print("\n" + "=" * 50)
    print("STEP 2: LOGIN")
    print("=" * 50)
    token = login(username, password)
    
    if token:
        print("\n" + "=" * 50)
        print("✅ SUCCESS!")
        print("=" * 50)
        print(f"\nYour authentication token:")
        print(f"\n{token}\n")
        print("📝 NEXT STEPS:")
        print(f"1. Open 'client.py' in your editor")
        print(f'2. Find the line: TOKEN = "..."')
        print(f'3. Replace it with: TOKEN = "{token}"')
        print(f"4. Save the file")
        print(f"5. Run: python client.py")
        print("=" * 50)
    else:
        print("\n❌ Login failed. Please check if the server is running.")
