import requests

# Check jobs in database
print("Checking jobs in database...")
response = requests.get('https://punjab-rozgar-api.onrender.com/api/v1/jobs/')

if response.status_code == 200:
    jobs = response.json()
    print(f"Total jobs found: {len(jobs)}")
    
    if jobs:
        print("\nJob details:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job.get('title', 'No title')}")
            print(f"   Status: {job.get('status', 'unknown')}")
            print(f"   Employer: {job.get('employer_id', 'unknown')}")
            print(f"   ID: {job.get('job_id', 'no-id')}")
            print(f"   Created: {job.get('created_at', 'unknown')}")
            print()
    else:
        print("No jobs found in database!")
        
        # Try to create some demo jobs
        print("Creating demo jobs...")
        demo_response = requests.get('https://punjab-rozgar-api.onrender.com/api/v1/auth/create-demo-jobs')
        if demo_response.status_code == 200:
            result = demo_response.json()
            print(f"Demo jobs result: {result}")
        else:
            print(f"Demo job creation failed: {demo_response.status_code}")

else:
    print(f"Error fetching jobs: {response.status_code} - {response.text}")