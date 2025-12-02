# Job Dashboard Visibility Issues - Troubleshooting Guide

## Problem
Jobs created by employers are not appearing in employee dashboard or admin dashboard.

## Root Causes Identified & Fixed

### 1. Admin Dashboard Issues (FIXED)
**Problem**: Admin dashboard was calling wrong endpoints
- ❌ Was calling: `/api/v1/jobs/recent`, `/api/v1/jobs/`, `/api/v1/jobs/featured`, `/api/v1/jobs/mock`
- ✅ Now calling: `/api/v1/admin/jobs` (primary), with fallbacks

**Fix Applied**: Updated `frontend/pages/dashboard/admin/jobs.html`
- Now uses proper admin endpoint with authentication
- Added proper headers with Bearer token
- Added fallback endpoints if admin endpoint fails

### 2. Data Field Mismatch Issues (FIXED)
**Problem**: Frontend expected different field names than backend provided
- Frontend expected: `views`, `application_count`
- Backend returned: `views_count`, `applications_count` (from different endpoints)

**Fix Applied**: Added data normalization in admin dashboard
- Maps various field names to consistent format
- Handles data from different API endpoints consistently

### 3. Backend Stats Query Error (FIXED)  
**Problem**: Admin stats endpoint looking for non-existent `Job.is_active` field
- ❌ Was using: `Job.is_active == True`
- ✅ Now using: `Job.status == JobStatus.ACTIVE`

**Fix Applied**: Updated `backend/app/api/v1/admin.py`

### 4. Missing Authentication (FIXED)
**Problem**: Dashboards weren't sending authentication headers
- Admin dashboard now includes proper Bearer token
- Employee dashboard already had this, but improved error handling

## Additional Improvements Made

### 1. Added Refresh Functionality
- Both dashboards now have refresh buttons
- Users can manually reload job data without page refresh

### 2. Better Error Handling
- Added console logging for debugging
- Better fallback mechanisms when endpoints fail
- User-friendly error messages

### 3. Enhanced Debugging
- Added sample data logging to console
- Better visibility into what data is being returned

## Testing Steps

1. **Test Job Creation**:
   ```bash
   cd "D:\cap pro\last\capstone-analytics"
   python test_dashboard_visibility.py
   ```

2. **Test Admin Dashboard**:
   - Login as admin
   - Go to admin jobs dashboard
   - Check browser console for logs
   - Verify jobs are displayed

3. **Test Employee Dashboard**:
   - Login as employer
   - Go to "My Jobs" section  
   - Check if newly created jobs appear
   - Use refresh button if needed

## API Endpoints Used

### For Admin Dashboard:
1. Primary: `GET /api/v1/admin/jobs` (with auth)
2. Fallback: `GET /api/v1/jobs/` (with auth)
3. Final fallback: `GET /api/v1/jobs/recent` (no auth)

### For Employee Dashboard:
1. Primary: `GET /api/v1/jobs/my-jobs` (with auth)
2. Fallback: `GET /api/v1/jobs/` (filter by employer_id)

### For Job Creation:
- `POST /api/v1/jobs/` (creates job with status=ACTIVE immediately)

## Browser Console Debugging

When testing, check browser console for:
- `Admin: Found X jobs from admin endpoint`
- `Found X employer jobs`
- Sample job data objects
- Any error messages

## Next Steps if Issues Persist

1. Check network connectivity to API server
2. Verify user authentication tokens are valid
3. Check API server logs for any errors
4. Ensure database connection is working
5. Verify job status is set to "active" in database

## Files Modified

1. `frontend/pages/dashboard/admin/jobs.html`
   - Fixed API endpoint calls
   - Added authentication headers
   - Added data normalization
   - Added refresh button

2. `frontend/pages/employer/jobs.html`  
   - Added refresh button
   - Enhanced debugging

3. `backend/app/api/v1/admin.py`
   - Fixed Job.is_active → Job.status query

4. `test_dashboard_visibility.py` (NEW)
   - Comprehensive test script for job creation and visibility