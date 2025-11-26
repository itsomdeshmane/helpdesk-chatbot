"""
Simple test script to verify backend is working correctly
Run this after starting the backend server
"""
import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_root():
    """Test if backend is running"""
    try:
        response = requests.get(BACKEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    try:
        print("\n🧪 Testing chat endpoint...")
        response = requests.post(
            f"{BACKEND_URL}/chat/query",
            json={
                "query": "What is an ERP system?",
                "tenant_id": "default"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working!")
            print(f"   Module detected: {data.get('module', 'N/A')}")
            print(f"   Response preview: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        print("   Possible issues:")
        print("   - OpenAI API key not configured")
        print("   - Slow internet connection")
        print("   - OpenAI API is down")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Backend Test Script")
    print("=" * 60)
    
    print("\n1️⃣ Testing if backend is running...")
    if not test_root():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend")
        print("   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("\n2️⃣ Testing chat functionality...")
    if test_chat():
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour backend is working correctly.")
        print("You can now use the frontend at http://localhost:3000")
    else:
        print("\n" + "=" * 60)
        print("⚠️  TESTS FAILED")
        print("=" * 60)
        print("\nPlease check:")
        print("1. Your .env file has OPENAI_API_KEY set")
        print("2. Your OpenAI key is valid")
        print("3. You have internet connection")
        print("\nFor more help, see QUICK_START.md")

if __name__ == "__main__":
    main()

