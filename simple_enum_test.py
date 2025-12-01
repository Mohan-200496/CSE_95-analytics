#!/usr/bin/env python3
"""
Simple test to understand the production database schema
"""

import requests
import json

BASE_URL = "https://cse-95-analytics.onrender.com"

def simple_test():
    print("🔍 Simple Production Test")
    print("=" * 30)
    
    # Test API health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test user creation with admin role (this usually works)
    print("\n🧪 Testing admin user creation...")
    admin_data = {
        "email": "test_admin@test.com",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "Admin",
        "role": "admin",
        "phone": "1234567890"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=admin_data)
        print(f"Admin registration status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Admin registration result: {result}")
        else:
            print(f"Admin registration failed: {response.text}")
    except Exception as e:
        print(f"Admin registration error: {e}")
    
    # Test with job_seeker role  
    print("\n🧪 Testing job_seeker user creation...")
    jobseeker_data = {
        "email": "test_jobseeker@test.com",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "JobSeeker",
        "role": "job_seeker",
        "phone": "1234567891"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=jobseeker_data)
        print(f"JobSeeker registration status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"JobSeeker registration result: {result}")
        else:
            print(f"JobSeeker registration failed: {response.text}")
    except Exception as e:
        print(f"JobSeeker registration error: {e}")
    
    # Test with employer role
    print("\n🧪 Testing employer user creation...")
    employer_data = {
        "email": "test_employer@test.com",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "Employer",
        "role": "employer",
        "phone": "1234567892"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=employer_data)
        print(f"Employer registration status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Employer registration result: {result}")
        else:
            print(f"Employer registration failed: {response.text}")
            # Try to extract the specific error
            try:
                error_data = response.json()
                print(f"Employer error details: {error_data}")
            except:
                print(f"Raw employer error: {response.text}")
    except Exception as e:
        print(f"Employer registration error: {e}")

if __name__ == "__main__":
    simple_test()