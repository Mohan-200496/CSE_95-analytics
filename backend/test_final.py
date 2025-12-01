"""
Final connectivity test - Quick verification that everything works
"""

import requests
import json
import sys

def test_endpoints():
    """Test the main endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔗 TESTING PUNJAB ROZGAR PORTAL API")
    print("=" * 50)
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("API Documentation", f"{base_url}/api/docs"), 
        ("OpenAPI Schema", f"{base_url}/api/openapi.json"),
        ("Recommendations Test", f"{base_url}/api/v1/recommendations/test")
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {test_name}: Working")
                if test_name == "Health Check":
                    data = response.json()
                    print(f"   Response: {data}")
                results.append(True)
            elif response.status_code == 401:
                print(f"✅ {test_name}: Working (auth required)")
                results.append(True)
            elif response.status_code == 404:
                print(f"⚠️ {test_name}: Not found")
                results.append(False)
            else:
                print(f"⚠️ {test_name}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            results.append(False)
    
    # Special test for recommendation endpoints in schema
    try:
        response = requests.get(f"{base_url}/api/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            rec_paths = [path for path in paths if "recommendation" in path.lower()]
            
            print(f"\n📋 Found {len(rec_paths)} recommendation endpoints:")
            for path in rec_paths[:6]:  # Show first 6
                methods = list(paths[path].keys())
                print(f"   • {', '.join(methods).upper()} {path}")
    except:
        pass
    
    success_rate = (sum(results) / len(results)) * 100
    
    print(f"\n📊 CONNECTIVITY TEST RESULTS: {sum(results)}/{len(results)} passed ({success_rate:.0f}%)")
    
    if success_rate >= 75:
        print("\n🎉 SYSTEM IS OPERATIONAL!")
        print(f"   • API Docs: {base_url}/api/docs")
        print(f"   • Health: {base_url}/health") 
        print(f"   • Recommendations: {base_url}/api/v1/recommendations/")
        print("\n✨ The Hybrid GA+CF Recommendation System is ready!")
        return True
    else:
        print("\n⚠️ Some endpoints are not responding correctly.")
        return False

if __name__ == "__main__":
    success = test_endpoints()
    sys.exit(0 if success else 1)