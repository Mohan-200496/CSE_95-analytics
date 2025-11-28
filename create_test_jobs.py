import sqlite3
import uuid
from datetime import datetime, timedelta
import json

# Connect to database
conn = sqlite3.connect('backend/punjab_rozgar.db')
cursor = conn.cursor()

# Get employer user_id
cursor.execute('SELECT user_id FROM users WHERE email = ? AND role = ?', ('employer@test.com', 'EMPLOYER'))
employer_result = cursor.fetchone()
if not employer_result:
    print('❌ No employer found')
    exit(1)

employer_user_id = employer_result[0]
print(f'✅ Found employer: {employer_user_id}')

# Sample jobs data
jobs_data = [
    {
        'title': 'Full Stack Developer',
        'description': 'We are looking for a skilled Full Stack Developer to join our team. The ideal candidate will have experience with React, Node.js, and databases.',
        'location_city': 'Chandigarh',
        'location_state': 'Chandigarh',
        'job_type': 'FULL_TIME',
        'category': 'Software Development',
        'salary_min': 50000,
        'salary_max': 80000,
        'experience_min': 2,
        'experience_max': 5,
        'skills_required': json.dumps(['React', 'Node.js', 'JavaScript', 'SQL']),
        'status': 'PENDING_APPROVAL'
    },
    {
        'title': 'Frontend Developer',
        'description': 'Join our frontend team to build amazing user interfaces. Experience with modern JavaScript frameworks required.',
        'location_city': 'Mohali',
        'location_state': 'Punjab',
        'job_type': 'FULL_TIME',
        'category': 'Frontend Development',
        'salary_min': 40000,
        'salary_max': 65000,
        'experience_min': 1,
        'experience_max': 3,
        'skills_required': json.dumps(['React', 'HTML', 'CSS', 'JavaScript']),
        'status': 'PENDING_APPROVAL'
    },
    {
        'title': 'Data Analyst',
        'description': 'Analyze business data to help make informed decisions. Strong analytical skills and experience with data tools required.',
        'location_city': 'Ludhiana',
        'location_state': 'Punjab',
        'job_type': 'FULL_TIME',
        'category': 'Data Analysis',
        'salary_min': 35000,
        'salary_max': 55000,
        'experience_min': 1,
        'experience_max': 4,
        'skills_required': json.dumps(['Python', 'SQL', 'Excel', 'Tableau']),
        'status': 'PENDING_APPROVAL'
    }
]

# Insert jobs
jobs_created = 0
for job_data in jobs_data:
    # Check if job already exists (by title and employer)
    cursor.execute('SELECT job_id FROM jobs WHERE title = ? AND employer_id = ?', (job_data['title'], employer_user_id))
    if cursor.fetchone():
        print(f'Skip existing: {job_data["title"]}')
        continue
    
    job_id = f'job_{uuid.uuid4().hex[:8]}'
    now = datetime.now()
    
    cursor.execute('''
        INSERT INTO jobs (
            job_id, title, description, employer_id, employer_name, employer_type,
            location_city, location_state, job_type, category,
            salary_min, salary_max, salary_currency, salary_period,
            experience_min, experience_max, skills_required,
            status, created_at, updated_at, application_deadline,
            remote_allowed, resume_required, application_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id,
        job_data['title'],
        job_data['description'],
        employer_user_id,
        'TechSoft Solutions',
        'private_company',
        job_data['location_city'],
        job_data['location_state'],
        job_data['job_type'],
        job_data['category'],
        job_data['salary_min'],
        job_data['salary_max'],
        'INR',
        'monthly',
        job_data['experience_min'],
        job_data['experience_max'],
        job_data['skills_required'],
        job_data['status'],
        now.isoformat(),
        now.isoformat(),
        (now + timedelta(days=30)).isoformat(),
        True,
        True,
        'online'
    ))
    
    jobs_created += 1
    print(f'Created: {job_data["title"]} (Status: {job_data["status"]})')

conn.commit()

print(f'\nCreated {jobs_created} new jobs for testing')
print('Jobs are in PENDING_APPROVAL status - admin needs to approve them')

# Show current jobs summary
cursor.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status')
job_stats = cursor.fetchall()
print('\nCurrent job statistics:')
for status, count in job_stats:
    print(f'  {status}: {count} jobs')

conn.close()