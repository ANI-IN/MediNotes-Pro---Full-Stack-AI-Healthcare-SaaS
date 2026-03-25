# Deployment Guide

## Overview

MediNotes Pro supports two deployment paths: Vercel (serverless) and AWS App Runner (containerized). Both produce a fully functional production deployment with HTTPS, but they differ in architecture, cost model, and operational characteristics.

---

## Path A: Vercel Deployment

### How Vercel Works With This Project

Vercel auto-detects two things in the repository:

1. **Next.js frontend** — Files in `pages/` are built and served as static pages with client-side JavaScript
2. **Python backend** — Files in `api/` are deployed as serverless Python functions

No `vercel.json` configuration file is needed for the full-stack setup (Day 2 onwards). Vercel's convention-based routing handles it automatically.

### Step-by-Step

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Link your project (first time only)
vercel link
# → Set up and link? Yes
# → Which scope? Your personal account
# → Link to existing project? No
# → Project name: medinotes-pro
# → Directory: . (current)

# 4. Add environment variables
vercel env add OPENAI_API_KEY
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
vercel env add CLERK_SECRET_KEY
vercel env add CLERK_JWKS_URL
# For each: paste value, select all environments

# 5. Deploy to preview
vercel .

# 6. Deploy to production
vercel --prod
```

### Vercel Architecture Details

- Frontend pages are served from Vercel's Edge CDN (global, fast)
- Python endpoints run as Vercel Serverless Functions (cold starts possible)
- Environment variables are injected at build time (public keys) and runtime (secret keys)
- HTTPS is automatic
- Custom domains can be added in the Vercel dashboard

### Vercel Limitations

- **60-second timeout**: Streaming responses that take longer than 60 seconds will be terminated. This can affect long AI generations. See the JWT timeout fix in `community_contributions/`.
- **Cold starts**: First request after inactivity may be slow (1-3 seconds) as the Python function initializes.
- **No persistent process**: Each request may run in a fresh environment. No in-memory caching between requests.

---

## Path B: AWS App Runner Deployment

### Prerequisites

1. AWS account with IAM user (`aiengineer`) configured
2. Docker Desktop installed and running
3. AWS CLI configured (`aws configure`)
4. ECR repository created (`consultation-app` or `medinotes-pro`)

### Step 1: Prepare for Static Export

Ensure `next.config.ts` has static export enabled:

```typescript
const nextConfig: NextConfig = {
  output: 'export',
  images: { unoptimized: true }
};
```

Ensure `pages/product.tsx` uses `/api/consultation` (not `/api`) for the API endpoint.

### Step 2: Create ECR Repository

```bash
# Via AWS Console:
# ECR → Create repository → Private → Name: medinotes-pro

# Or via CLI:
aws ecr create-repository --repository-name medinotes-pro --region $DEFAULT_AWS_REGION
```

### Step 3: Build and Push Docker Image

```bash
# Load environment variables
export $(cat .env.local | grep -v '^#' | xargs)

# Authenticate Docker to ECR
aws ecr get-login-password --region $DEFAULT_AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com

# Build (ALWAYS use --platform linux/amd64, especially on Apple Silicon)
docker build \
  --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t medinotes-pro .

# Tag
docker tag medinotes-pro:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest

# Push
docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest
```

### Step 4: Create App Runner Service

In AWS Console → App Runner → Create service:

1. **Source**: Container registry → Amazon ECR → Select your image
2. **Deployment**: Manual trigger, Create new service role
3. **Service name**: `medinotes-pro-service`
4. **CPU/Memory**: 0.25 vCPU / 0.5 GB
5. **Port**: 8000
6. **Environment variables**:
   - `CLERK_SECRET_KEY` = your value
   - `CLERK_JWKS_URL` = your value
   - `OPENAI_API_KEY` = your value
7. **Auto scaling**: Min 1, Max 1 (cost control)
8. **Health check**: HTTP, path `/health`, interval 20s

Click Create & deploy. Wait 5-10 minutes.

### Step 5: Set Up Budget Alerts

Create three AWS Budgets:
- `early-warning` at $1
- `caution-budget` at $5
- `stop-budget` at $10

Each sends email alerts at 85% and 100% of threshold.

### Updating the Deployment

After code changes:

```bash
# Rebuild
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t medinotes-pro .

# Tag and push
docker tag medinotes-pro:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest
docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest

# Deploy in App Runner console → Click Deploy
```

### AWS Cost Management

| Resource | Estimated Cost |
|----------|---------------|
| App Runner (1 instance, 0.25 vCPU) | ~$5/month |
| ECR image storage | ~$0.10/month |
| CloudWatch logs | Free tier usually covers it |
| **Total** | **~$5-6/month** |

To pause and stop charges: App Runner → Select service → Actions → Pause service.

---

## Deployment Comparison Summary

| Aspect | Vercel | AWS App Runner |
|--------|--------|----------------|
| Setup Complexity | Low (CLI commands) | Medium (ECR, IAM, App Runner config) |
| Cost | Free tier available | ~$5-10/month minimum |
| Cold Starts | Yes (serverless) | No (persistent instance) |
| Streaming Timeout | 60 seconds | Configurable (longer) |
| Custom Domain | Dashboard toggle | DNS configuration |
| Scaling | Automatic | Configurable min/max |
| Monitoring | Vercel Dashboard | CloudWatch |
| CI/CD | Git push (automatic) | Manual or GitHub Actions |
