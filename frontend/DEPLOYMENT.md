# SchoolOps Deployment Guide - Vercel

## Prerequisites

1. **Vercel Account**: Create an account at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Node.js**: Version 18 or higher

## Deployment Methods

### Method 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy to Vercel
vercel
```

Follow the interactive prompts:
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No** (or Yes if already linked)
- Project name: **schoolops** (or your preferred name)
- Directory? **./**
- Want to modify settings? **No** (Vercel auto-detects Next.js)

### Method 2: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure settings:
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
5. Click **Deploy**

## Environment Variables

Add these environment variables in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | Your backend API URL | All |
| `NEXT_PUBLIC_GRAPHQL_URL` | Your GraphQL endpoint | All |

Example values for development:
- `NEXT_PUBLIC_API_URL`: `http://localhost:8000`
- `NEXT_PUBLIC_GRAPHQL_URL`: `http://localhost:8000/graphql`

For production, replace with your actual backend URL.

## Deployment Steps

### 1. Push to GitHub

```bash
# In the project root
cd /workspace/schoolops-system

# Add all files
git add .

# Commit changes
git commit -m "Add landing page and Vercel config"

# Push to GitHub
git push origin main
```

### 2. Connect to Vercel

1. Visit [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Select your `schoolops-system` repository
4. Click **"Import"**

### 3. Configure Settings

In the Vercel project configuration:

```
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### 4. Add Environment Variables

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### 5. Deploy

Click **"Deploy"** and wait for the build to complete.

## Custom Domain (Optional)

1. In Vercel Dashboard, go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS records as instructed by Vercel

## Post-Deployment

After deployment, your site will be available at:
- **Production**: `https://schoolops.vercel.app` (or your custom domain)
- **Landing Page**: `https://schoolops.vercel.app/`
- **Dashboard**: `https://schoolops.vercel.app/dashboard`

## Troubleshooting

### Build Fails

1. Check build logs in Vercel Dashboard
2. Ensure all dependencies are in `package.json`
3. Verify TypeScript types are correct

### API Not Connecting

1. Check environment variables are set correctly
2. Verify CORS settings on your backend
3. Ensure backend is deployed and accessible

### 404 on Dashboard Route

1. Ensure the `/dashboard` route exists in `src/app/dashboard/page.tsx`
2. Check that `next.config.js` is configured correctly

## Useful Commands

```bash
# Build locally
cd frontend && npm run build

# Test production build locally
cd frontend && npm run start

# Check for deployment issues
cd frontend && npm run lint
```

## Next Steps

1. **Deploy Backend**: Deploy your FastAPI backend to:
   - Vercel (using serverless functions)
   - Railway
   - Render
   - AWS/GCP/Azure

2. **Update Environment Variables**: Set the production API URL

3. **Configure SSL**: Vercel automatically provides SSL for custom domains

4. **Set up Preview Deployments**: Vercel automatically creates preview deployments for pull requests
