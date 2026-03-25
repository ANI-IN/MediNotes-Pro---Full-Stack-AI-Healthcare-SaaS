# Setup Guide

## Prerequisites

### Required Software

| Software | Minimum Version | Installation |
|----------|---------------|-------------|
| Node.js | 18.x | [nodejs.org/en/download](https://nodejs.org/en/download) |
| Python | 3.9 | Included on most systems; verify with `python3 --version` |
| npm | 9.x | Included with Node.js |
| Git | 2.x | [git-scm.com](https://git-scm.com) |

### Optional Software (AWS Deployment)

| Software | Version | Installation |
|----------|---------|-------------|
| Docker Desktop | 26.x+ | [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop) |
| AWS CLI | 2.x | [aws.amazon.com/cli](https://aws.amazon.com/cli) |
| Vercel CLI | Latest | `npm install -g vercel` |

### Required Accounts

| Service | Sign Up URL | What You Need |
|---------|-----------|--------------|
| OpenAI | [platform.openai.com](https://platform.openai.com) | API key (`sk-proj-...`), $5 minimum credit |
| Clerk | [clerk.com](https://clerk.com) | Publishable key, secret key, JWKS URL |
| Vercel | [vercel.com](https://vercel.com) | Account for serverless deployment |
| AWS | [aws.amazon.com](https://aws.amazon.com) | Account for container deployment (optional) |

---

## Step-by-Step Setup

### 1. Clone and Install

```bash
git clone https://github.com/your-username/medinotes-pro.git
cd medinotes-pro

# Install frontend dependencies
npm install

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI

1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to Settings → Organization → Billing → Add $5 minimum payment
3. Disable Auto Recharge
4. Go to Settings → Organization → API Keys → Create new secret key
5. Copy the key (starts with `sk-proj-`)

### 3. Configure Clerk

1. Go to [clerk.com](https://clerk.com) and create an account
2. Create a new application named "MediNotes Pro"
3. Enable sign-in providers: Email, Google, GitHub
4. From the Clerk dashboard, copy:
   - **Publishable Key** (starts with `pk_test_`)
   - **Secret Key** (starts with `sk_test_`)
5. Go to Configure → API Keys → copy the **JWKS URL**

### 4. Configure Clerk Billing (Subscription)

1. In Clerk Dashboard → Configure → Subscription Plans
2. Click Enable Billing
3. Create a plan:
   - Name: `Premium Subscription`
   - Key: `premium_subscription` (must match exactly)
   - Price: $10/month
4. Save the plan

### 5. Create Environment File

Create `.env.local` in the project root:

```bash
# Copy from .env.example
cp .env.example .env.local

# Then fill in your values:
OPENAI_API_KEY=sk-proj-your-key-here
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your-key-here
CLERK_SECRET_KEY=sk_test_your-key-here
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
```

Verify `.env.local` is in `.gitignore` (it should be by default).

### 6. Verify Installation

```bash
# Check Node.js
node --version    # Should show 18.x or higher

# Check Python
python3 --version # Should show 3.9+

# Check npm packages installed
npm list react-markdown  # Should show version

# Check Python packages
pip show fastapi openai   # Should show package info
```

---

## Running Locally

### Option A: Vercel Dev Server

```bash
npx vercel dev
```

This starts a local development server at `http://localhost:3000` that mimics the Vercel production environment, routing `/api` requests to the Python backend.

Note: You need to link the project to Vercel first (`vercel link`) and add environment variables to Vercel (`vercel env add`) for the backend to access secrets.

### Option B: Docker Container

```bash
# Load environment variables
export $(cat .env.local | grep -v '^#' | xargs)

# Build
docker build \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t medinotes-pro .

# Run
docker run -p 8000:8000 \
  -e CLERK_SECRET_KEY="$CLERK_SECRET_KEY" \
  -e CLERK_JWKS_URL="$CLERK_JWKS_URL" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  medinotes-pro
```

Access at `http://localhost:8000`.

---

## Troubleshooting Setup

### "Module not found" errors

```bash
rm -rf node_modules
npm install
```

### Python dependency errors

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Clerk sign-in modal not appearing

- Verify `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_`
- Check that `ClerkProvider` wraps the app in `pages/_app.tsx`
- Clear browser cache and cookies

### OpenAI API key not working

- Verify key starts with `sk-proj-`
- Check that you have credit balance at platform.openai.com
- Verify Auto Recharge is disabled (to control costs)

### Docker build fails

- Ensure Docker Desktop is running
- Check available disk space (build needs ~2GB)
- On Apple Silicon: always use `--platform linux/amd64` flag
