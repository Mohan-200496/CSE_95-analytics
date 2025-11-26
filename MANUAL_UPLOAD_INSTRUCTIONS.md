# Manual GitHub Upload Instructions

Since Git is not installed on your system, here's how to upload your project manually:

## Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `CSE_95-analytics`
3. Description: `Punjab Rozgar Analytics Portal - Employment analytics platform for Punjab state`
4. Make it **PUBLIC**
5. **Check "Add a README file"** (we'll replace it)
6. Click "Create repository"

## Step 2: Upload Files
1. In your new repository, click "uploading an existing file"
2. Drag and drop ALL files from `d:\cap pro\last\capstone-analytics\` folder
3. **Important files to upload:**
   - All `backend/` folder contents
   - All `frontend/` folder contents  
   - `README.md`
   - `LICENSE`
   - `.gitignore`
   - `CONTRIBUTING.md`
   - `CHANGELOG.md`
   - `docker-compose.yml`
   - All `.bat` files

## Step 3: Commit Changes
1. Scroll down to "Commit changes" section
2. Commit message: `Initial commit: CSE_95 Analytics - Punjab Rozgar Portal`
3. Description: `Complete employment analytics platform with FastAPI backend and vanilla JS frontend`
4. Click "Commit changes"

## Alternative: Use GitHub Desktop
1. Download GitHub Desktop from https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click "Clone a repository from the Internet"
4. Choose your repository
5. Copy all project files to the cloned folder
6. Commit and push changes

## Files Structure to Upload:
```
CSE_95-analytics/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── pages/
│   ├── js/
│   ├── api/
│   └── assets/
├── README.md
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docker-compose.yml
└── *.bat files
```

Your repository will be available at: https://github.com/YOURUSERNAME/CSE_95-analytics