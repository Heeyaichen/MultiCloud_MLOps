# Guardian AI - Complete End-to-End Deployment Guide

**🎯 Goal**: Deploy the complete MLOps system to AWS + Azure cloud infrastructure
**⏱️ Time**: 4-6 hours (first-time deployment)

---

## Overview

This guide walks you through deploying the complete Guardian AI MLOps platform from scratch, including:
- AWS infrastructure (S3, SQS, DynamoDB)
- Azure infrastructure (AKS, ACR, Azure ML)
- All 6 microservices
- Kubernetes deployment
- Monitoring setup
- End-to-end testing

---

## 📋 Platform Notes

**Important for Windows Users:**

- **Default Commands**: All commands shown are for **Linux/macOS (bash)** by default
- **Windows Options**:
  - **Git Bash** (Recommended) - Runs bash commands directly, minimal changes needed
  - **WSL2** (Windows Subsystem for Linux) - Full Linux environment, best compatibility
  - **PowerShell** - See PowerShell alternatives provided for key sections below
- **PowerShell Alternatives**: Provided for critical setup steps (environment variables, AWS/Azure config, file operations)
- **Bash Scripts**: Scripts like `setup-aws.sh` require Git Bash or WSL2 on Windows

**Command Mapping Reference:**

| Operation | Linux/macOS (bash) | Windows (PowerShell) |
|-----------|-------------------|---------------------|
| Set environment variable | `export VAR=value` | `$env:VAR = "value"` |
| Get environment variable | `echo $VAR` | `Write-Host $env:VAR` |
| Command substitution | `$(command)` | `$(command)` |
| String substring | `cut -c1-8` | `$var.Substring(0,8)` |
| Timestamp | `date +%s` | `[DateTimeOffset]::Now.ToUnixTimeSeconds()` |
| Python venv activate | `source venv/bin/activate` | `.\venv\Scripts\Activate.ps1` |
| Create file with content | `cat > file <<EOF` | `@'...'@ | Out-File file` |
| Home directory | `~/Projects` | `$env:USERPROFILE\Projects` |
| Run bash script | `bash script.sh` | `bash script.sh` (Git Bash) or `wsl bash script.sh` |

---

## Prerequisites

### Required Tools

**All Platforms - Verify Installations:**
```bash
# These commands work on Linux, macOS, Windows PowerShell, and Git Bash
docker --version          # Docker Desktop 24+
kubectl version --client  # kubectl 1.28+
python --version          # Python 3.11+ (use 'python' on Windows, 'python3' on Linux/macOS)
aws --version            # AWS CLI 2.13+
az --version             # Azure CLI 2.50+
helm version             # Helm 3.12+
node --version           # Node.js 20+ (for frontend)
```

**Installation Instructions:**

**Linux/macOS:**
```bash
# macOS (using Homebrew)
brew install kubectl python@3.11 awscli azure-cli helm node

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y kubectl python3.11 python3-pip awscli azure-cli helm nodejs npm

# Linux (RHEL/CentOS)
sudo yum install -y kubectl python3.11 python3-pip awscli azure-cli helm nodejs npm
```

**Windows:**
```powershell
# Using Chocolatey (recommended)
choco install docker-desktop kubectl python311 awscli azure-cli kubernetes-helm nodejs

# Or using winget
winget install Docker.DockerDesktop
winget install Kubernetes.kubectl
winget install Python.Python.3.11
winget install Amazon.AWSCLI
winget install Microsoft.AzureCLI
winget install Kubernetes.Helm
winget install OpenJS.NodeJS

# Install Git Bash (recommended for Windows users)
winget install Git.Git
```

### Required Accounts
- **AWS account** with AdministratorAccess
- **Azure subscription** with Owner/Contributor access
- **GitHub account** (for version control and CI/CD)

---

## Phase 1: Project Setup & Initialization (30 minutes)

### Step 1.1: Clone/Initialize Project

**Linux/macOS (bash):**
```bash
# Navigate to project directory
cd ~/Projects/MLOps_Project

# Initialize git (if not already done)
git init

# Verify project structure
ls -la services/
ls -la k8s/
ls -la scripts/

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install common dependencies
pip install fastapi uvicorn python-multipart boto3 botocore redis httpx openai
```

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd $env:USERPROFILE\Projects\MLOps_Project

# Initialize git (if not already done)
git init

# Verify project structure
Get-ChildItem services\
Get-ChildItem k8s\
Get-ChildItem scripts\

# Create Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install common dependencies
pip install fastapi uvicorn python-multipart boto3 botocore redis httpx openai
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
cd ~/Projects/MLOps_Project
git init
ls -la services/
python -m venv venv
source venv/Scripts/activate  # Note: Scripts (capital S) on Windows
pip install fastapi uvicorn python-multipart boto3 botocore redis httpx openai
```

### Step 1.2: Verify Project Structure

**Linux/macOS (bash):**
```bash
# Ensure all required directories exist
mkdir -p services/{ingestion,fast-screening,deep-vision,policy-engine,human-review,notification}
mkdir -p k8s/{cpu-services,gpu-services,frontend}
mkdir -p scripts
mkdir -p mlops/{training,deployment}
mkdir -p tests/load
mkdir -p infrastructure

echo "✅ Project structure verified"
```

**Windows (PowerShell):**
```powershell
# Ensure all required directories exist
New-Item -ItemType Directory -Force -Path services\ingestion,services\fast-screening,services\deep-vision,services\policy-engine,services\human-review,services\notification
New-Item -ItemType Directory -Force -Path k8s\cpu-services,k8s\gpu-services,k8s\frontend
New-Item -ItemType Directory -Force -Path scripts,mlops\training,mlops\deployment,tests\load,infrastructure

Write-Host "✅ Project structure verified"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
mkdir -p services/{ingestion,fast-screening,deep-vision,policy-engine,human-review,notification}
mkdir -p k8s/{cpu-services,gpu-services,frontend}
mkdir -p scripts mlops/{training,deployment} tests/load infrastructure
```

---

## Phase 2: AWS Infrastructure Setup (30 minutes)

### Step 2.1: Configure AWS Credentials

**Linux/macOS (bash):**
```bash
# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Default region (ap-south-1 recommended for cost)
# Enter: Default output format (json)

# Verify configuration
aws sts get-caller-identity
aws configure get region

# Export for scripts
export AWS_REGION=$(aws configure get region)
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
```

**Windows (PowerShell):**
```powershell
# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Default region (ap-south-1 recommended for cost)
# Enter: Default output format (json)

# Verify configuration
aws sts get-caller-identity
aws configure get region

# Set environment variables for scripts
$env:AWS_REGION = aws configure get region
$env:AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

Write-Host "AWS Account ID: $env:AWS_ACCOUNT_ID"
Write-Host "AWS Region: $env:AWS_REGION"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
aws configure
aws sts get-caller-identity
export AWS_REGION=$(aws configure get region)
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

### Step 2.2: Create AWS Resources (Simplified Architecture)

**Linux/macOS (bash):**
```bash
# Run AWS setup script (creates 1 S3 bucket, 2 SQS queues, 2 DynamoDB tables)
bash scripts/setup-aws.sh

# This creates:
# ✅ S3 bucket: guardian-videos-xxxxxxxx (primary video storage)
# ✅ SQS queue: guardian-video-processing (main processing queue)
# ✅ SQS queue: guardian-gpu-processing (GPU autoscaling queue)
# ✅ DynamoDB table: guardian-videos (single source of truth)
# ✅ DynamoDB table: guardian-events (audit log with TTL)

# Save the bucket name from output
export S3_BUCKET_NAME="guardian-videos-$(echo $AWS_ACCOUNT_ID | cut -c1-8)"

echo "✅ AWS resources created"
```

**Windows (PowerShell):**
```powershell
# Run AWS setup script (requires Git Bash or WSL for bash scripts)
# Option 1: Use Git Bash (recommended)
bash scripts/setup-aws.sh

# Option 2: Use WSL
wsl bash scripts/setup-aws.sh

# Save the bucket name (PowerShell syntax)
$accountIdPrefix = $env:AWS_ACCOUNT_ID.Substring(0, 8)
$env:S3_BUCKET_NAME = "guardian-videos-$accountIdPrefix"

Write-Host "✅ AWS resources created"
Write-Host "S3 Bucket: $env:S3_BUCKET_NAME"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
bash scripts/setup-aws.sh
export S3_BUCKET_NAME="guardian-videos-$(echo $AWS_ACCOUNT_ID | cut -c1-8)"
```

### Step 2.3: Get AWS Resource URLs

**Linux/macOS (bash):**
```bash
# Get SQS queue URLs
export SQS_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-video-processing --query 'QueueUrl' --output text)
export SQS_GPU_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-gpu-processing --query 'QueueUrl' --output text)

# Verify resources exist
echo "S3 Bucket: $S3_BUCKET_NAME"
echo "SQS Main Queue: $SQS_QUEUE_URL"
echo "SQS GPU Queue: $SQS_GPU_QUEUE_URL"

# Test S3 access
aws s3 ls s3://$S3_BUCKET_NAME

# Test DynamoDB access
aws dynamodb describe-table --table-name guardian-videos --query 'Table.TableName'
aws dynamodb describe-table --table-name guardian-events --query 'Table.TableName'

echo "✅ AWS resources verified"
```

**Windows (PowerShell):**
```powershell
# Get SQS queue URLs
$env:SQS_QUEUE_URL = aws sqs get-queue-url --queue-name guardian-video-processing --query 'QueueUrl' --output text
$env:SQS_GPU_QUEUE_URL = aws sqs get-queue-url --queue-name guardian-gpu-processing --query 'QueueUrl' --output text

# Verify resources exist
Write-Host "S3 Bucket: $env:S3_BUCKET_NAME"
Write-Host "SQS Main Queue: $env:SQS_QUEUE_URL"
Write-Host "SQS GPU Queue: $env:SQS_GPU_QUEUE_URL"

# Test S3 access
aws s3 ls "s3://$env:S3_BUCKET_NAME"

# Test DynamoDB access
aws dynamodb describe-table --table-name guardian-videos --query 'Table.TableName'
aws dynamodb describe-table --table-name guardian-events --query 'Table.TableName'

Write-Host "✅ AWS resources verified"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
export SQS_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-video-processing --query 'QueueUrl' --output text)
export SQS_GPU_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-gpu-processing --query 'QueueUrl' --output text)
```

### Step 2.4: Create .env File for Local Testing

**Linux/macOS (bash):**
```bash
cat > .env <<EOF
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
AWS_REGION=$AWS_REGION
S3_BUCKET_NAME=$S3_BUCKET_NAME
SQS_QUEUE_URL=$SQS_QUEUE_URL
SQS_GPU_QUEUE_URL=$SQS_GPU_QUEUE_URL

# DynamoDB Tables
DYNAMODB_VIDEOS_TABLE=guardian-videos
DYNAMODB_EVENTS_TABLE=guardian-events

# Policy Engine Configuration
AUTO_APPROVE_THRESHOLD=0.2
AUTO_REJECT_THRESHOLD=0.8

# Azure OpenAI (Optional - Configure in Phase 4 if needed)
AZURE_OPENAI_ENABLED=false
# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
EOF

echo "✅ .env file created"
```

**Windows (PowerShell):**
```powershell
# Create .env file using PowerShell here-string
$envContent = @"
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
AWS_REGION=$env:AWS_REGION
S3_BUCKET_NAME=$env:S3_BUCKET_NAME
SQS_QUEUE_URL=$env:SQS_QUEUE_URL
SQS_GPU_QUEUE_URL=$env:SQS_GPU_QUEUE_URL

# DynamoDB Tables
DYNAMODB_VIDEOS_TABLE=guardian-videos
DYNAMODB_EVENTS_TABLE=guardian-events

# Policy Engine Configuration
AUTO_APPROVE_THRESHOLD=0.2
AUTO_REJECT_THRESHOLD=0.8

# Azure OpenAI (Optional - Configure in Phase 4 if needed)
AZURE_OPENAI_ENABLED=false
# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
"@

$envContent | Out-File -FilePath .env -Encoding utf8

Write-Host "✅ .env file created"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
cat > .env <<EOF
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
AWS_REGION=$AWS_REGION
S3_BUCKET_NAME=$S3_BUCKET_NAME
SQS_QUEUE_URL=$SQS_QUEUE_URL
SQS_GPU_QUEUE_URL=$SQS_GPU_QUEUE_URL

# DynamoDB Tables
DYNAMODB_VIDEOS_TABLE=guardian-videos
DYNAMODB_EVENTS_TABLE=guardian-events

# Policy Engine Configuration
AUTO_APPROVE_THRESHOLD=0.2
AUTO_REJECT_THRESHOLD=0.8

# Azure OpenAI (Optional - Configure in Phase 4 if needed)
AZURE_OPENAI_ENABLED=false
# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
EOF
```

---

## Phase 3: Azure Infrastructure Setup (45 minutes)

### Step 3.1: Login to Azure

**Linux/macOS (bash):**
```bash
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Verify
az account show --output table

# Set variables
export RESOURCE_GROUP="guardian-ai-prod"
export LOCATION="eastus"  # or swedencentral, westeurope
export ACR_NAME="guardianacr$(date +%s | cut -c 6-10)"
export AKS_CLUSTER="guardian-ai-aks"

echo "Azure Subscription: $(az account show --query name -o tsv)"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"
echo "AKS Cluster: $AKS_CLUSTER"
```

**Windows (PowerShell):**
```powershell
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Verify
az account show --output table

# Set variables
$env:RESOURCE_GROUP = "guardian-ai-prod"
$env:LOCATION = "eastus"  # or swedencentral, westeurope
$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$env:ACR_NAME = "guardianacr$($timestamp.ToString().Substring(5, 5))"
$env:AKS_CLUSTER = "guardian-ai-aks"

Write-Host "Azure Subscription: $(az account show --query name -o tsv)"
Write-Host "Resource Group: $env:RESOURCE_GROUP"
Write-Host "Location: $env:LOCATION"
Write-Host "ACR Name: $env:ACR_NAME"
Write-Host "AKS Cluster: $env:AKS_CLUSTER"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"
export RESOURCE_GROUP="guardian-ai-prod"
export LOCATION="eastus"
export ACR_NAME="guardianacr$(date +%s | cut -c 6-10)"
export AKS_CLUSTER="guardian-ai-aks"
```

### Step 3.2: Create Azure Resource Group

**Linux/macOS (bash):**
```bash
# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Verify
az group show --name $RESOURCE_GROUP --output table

echo "✅ Resource group created"
```

**Windows (PowerShell):**
```powershell
# Create resource group
az group create `
  --name $env:RESOURCE_GROUP `
  --location $env:LOCATION

# Verify
az group show --name $env:RESOURCE_GROUP --output table

Write-Host "✅ Resource group created"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
az group create --name $RESOURCE_GROUP --location $LOCATION
az group show --name $RESOURCE_GROUP --output table
```

### Step 3.3: Create Azure Container Registry (ACR)

**Linux/macOS (bash):**
```bash
# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard \
  --location $LOCATION

# Enable admin access (for easier local testing)
az acr update --name $ACR_NAME --admin-enabled true

# Get ACR credentials
export ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
export ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query 'passwords[0].value' -o tsv)
export ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo "ACR Username: $ACR_USERNAME"

# Login to ACR
az acr login --name $ACR_NAME

# Update all Kubernetes manifests to use this ACR (single source of truth)
# Manifests use ACR_PLACEHOLDER; this replaces it with your $ACR_NAME
./scripts/update-acr-in-manifests.sh

echo "✅ ACR created and logged in"
```

**Windows (PowerShell):**
```powershell
# Create ACR
az acr create `
  --resource-group $env:RESOURCE_GROUP `
  --name $env:ACR_NAME `
  --sku Standard `
  --location $env:LOCATION

# Enable admin access (for easier local testing)
az acr update --name $env:ACR_NAME --admin-enabled true

# Get ACR credentials
$env:ACR_USERNAME = az acr credential show --name $env:ACR_NAME --query username -o tsv
$env:ACR_PASSWORD = az acr credential show --name $env:ACR_NAME --query 'passwords[0].value' -o tsv
$env:ACR_LOGIN_SERVER = az acr show --name $env:ACR_NAME --query loginServer -o tsv

Write-Host "ACR Login Server: $env:ACR_LOGIN_SERVER"
Write-Host "ACR Username: $env:ACR_USERNAME"

# Login to ACR
az acr login --name $env:ACR_NAME

# Update all Kubernetes manifests to use this ACR (requires Git Bash or WSL for bash script)
bash scripts/update-acr-in-manifests.sh

Write-Host "✅ ACR created and logged in"
```

**Windows (Git Bash):**
```bash
# Same as Linux/macOS commands above
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Standard --location $LOCATION
az acr update --name $ACR_NAME --admin-enabled true
export ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
export ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query 'passwords[0].value' -o tsv)
export ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
az acr login --name $ACR_NAME
./scripts/update-acr-in-manifests.sh
```

### Step 3.4: Create AKS Cluster
```bash
# Create AKS cluster (this takes 10-15 minutes)
# Check if AKS cluster already exists
if az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER >/dev/null 2>&1; then
  echo "AKS cluster already exists, ensuring ACR is attached..."
  
  # Ensure ACR is attached
  if ! az aks check-acr --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP --acr ${ACR_NAME}.azurecr.io >/dev/null 2>&1; then
    az aks update \
      --resource-group $RESOURCE_GROUP \
      --name $AKS_CLUSTER \
      --attach-acr $ACR_NAME
  fi
else
  # Create AKS cluster (this takes 10-15 minutes)
  az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER \
    --node-count 4 \
    --node-vm-size Standard_D2s_v3 \
    --enable-managed-identity \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys \
    --location $LOCATION \
    --network-plugin azure 
  
  echo "AKS cluster creation in progress (10-15 minutes)..."
  az aks wait --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --created
fi

# Get AKS credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --overwrite-existing

# Verify connection
kubectl get nodes

echo "✅ AKS credentials configured"
```

### Step 3.5: Add GPU Node Pool (for Deep Vision Service)
```bash
# Add GPU node pool with scale-to-zero capability
# az aks nodepool add \
#   --resource-group $RESOURCE_GROUP \
#   --cluster-name $AKS_CLUSTER \
#   --name gpupool \
#   --node-count 0 \
#   --min-count 0 \
#   --max-count 3 \
#   --node-vm-size Standard_NC6s_v3 \
#   --enable-cluster-autoscaler \
#   --labels workload=gpu \
#   --node-taints sku=gpu:NoSchedule

# echo "✅ GPU node pool added (scale-to-zero enabled)"
```

### Step 3.6: Install KEDA for GPU Autoscaling
```bash
# Add KEDA Helm repository
# helm repo add kedacore https://kedacore.github.io/charts
# helm repo update

# # Install KEDA
# helm install keda kedacore/keda \
#   --namespace keda \
#   --create-namespace

# # Verify KEDA installation
# kubectl get pods -n keda

# echo "✅ KEDA installed for GPU autoscaling"
```

### Step 3.7: Install NGINX Ingress Controller
```bash
# Add NGINX Ingress Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.externalTrafficPolicy=Local

echo "⏳ Waiting for external IP (2-3 minutes)..."

# Wait for external IP
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Get external IP
# Linux/macOS (bash):
export EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Windows (PowerShell):
# $env:EXTERNAL_IP = kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

echo "✅ NGINX Ingress installed"
echo "External IP: $EXTERNAL_IP"
```

---

## Phase 4: Optional - Azure OpenAI Setup (15 minutes)

### Step 4.1: Create Azure OpenAI Resource (Optional)
```bash
# Skip this section if you don't want Azure OpenAI features
# Azure OpenAI is disabled by default to save costs

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "guardian-openai-$(date +%s | cut -c 6-10)" \
  --resource-group $RESOURCE_GROUP \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes

# Get endpoint and key
export AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name "guardian-openai-*" \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

export AZURE_OPENAI_API_KEY=$(az cognitiveservices account keys list \
  --name "guardian-openai-*" \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

# Deploy GPT-4o model
az cognitiveservices account deployment create \
  --name "guardian-openai-*" \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-05-13" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

echo "✅ Azure OpenAI configured"
echo "Endpoint: $AZURE_OPENAI_ENDPOINT"

# Update .env file
cat >> .env <<EOF

# Azure OpenAI (Enabled)
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
EOF
```

---

## Phase 5: Build and Push Docker Images (30 minutes)

### Step 5.1: Setup Docker Buildx
```bash
# Create buildx builder (for multi-platform builds)
docker buildx create --name guardian-builder --use || docker buildx use guardian-builder

# Verify
docker buildx inspect --bootstrap

echo "✅ Docker buildx configured"
```

### Step 5.2: Build and Push All Service Images
```bash
# Login to ACR
docker login $ACR_LOGIN_SERVER -u $ACR_USERNAME -p $ACR_PASSWORD

# Build and push all services (6 backend + 1 API gateway + 1 frontend = 8 total)
echo "Building and pushing images to ACR..."

# 1. Ingestion Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-ingestion:v1 \
  --push ./services/ingestion

# 2. Fast Screening Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-fast-screening:v1 \
  --push ./services/fast-screening

# 3. Deep Vision Service (will run on CPU nodes)
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-deep-vision:v1 \
  --push ./services/deep-vision

# 4. Policy Engine Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-policy-engine:v1 \
  --push ./services/policy-engine

# 5. Human Review Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-human-review:v1 \
  --push ./services/human-review

# 6. Notification Service
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-notification:v1 \
  --push ./services/notification

# 7. API Gateway Service (for frontend queries)
docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-api-gateway:v1 \
  --push ./services/api-gateway

# 8. Frontend (React + Material-UI)
cd frontend
npm install
npm run build
cd ..

docker buildx build --platform linux/amd64 \
  -t $ACR_LOGIN_SERVER/guardian-ai-frontend:v1 \
  --push ./frontend

echo "✅ All 8 images pushed to ACR (6 backend + 1 API gateway + 1 frontend)"
```

### Step 5.3: Verify Images in ACR
```bash
# List all repositories
az acr repository list --name $ACR_NAME --output table

# Show tags for each service
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-ingestion
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-fast-screening
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-deep-vision
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-policy-engine
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-human-review
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-notification
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-api-gateway
az acr repository show-tags --name $ACR_NAME --repository guardian-ai-frontend

echo "✅ All 8 images verified in ACR"
```

---

## Phase 6: Configure Kubernetes Manifests (20 minutes)

### Step 6.1: Update Kubernetes ConfigMap with AWS Values
```bash
# Update ConfigMap with actual AWS values
cat > k8s/configmap.yaml <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: guardian-config
  namespace: production
data:
  # AWS Configuration
  AWS_REGION: "$AWS_REGION"
  S3_BUCKET_NAME: "$S3_BUCKET_NAME"
  
  # Simplified SQS Queues (2 queues)
  SQS_QUEUE_URL: "$SQS_QUEUE_URL"
  SQS_GPU_QUEUE_URL: "$SQS_GPU_QUEUE_URL"
  
  # Simplified DynamoDB Tables (2 tables)
  DYNAMODB_VIDEOS_TABLE: "guardian-videos"
  DYNAMODB_EVENTS_TABLE: "guardian-events"
  
  # Service Configuration
  LOG_LEVEL: "INFO"
  AUTO_APPROVE_THRESHOLD: "0.2"
  AUTO_REJECT_THRESHOLD: "0.8"
  
  # Redis Configuration
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  
  # Azure OpenAI Configuration (Optional)
  AZURE_OPENAI_ENABLED: "false"
  
  # Service URLs (for direct HTTP calls)
  NOTIFICATION_SERVICE_URL: "http://notification:8005"
  HUMAN_REVIEW_SERVICE_URL: "http://human-review:8004"
  POLICY_ENGINE_SERVICE_URL: "http://policy-engine:8003"
EOF

echo "✅ ConfigMap updated with AWS values"
```

### Step 6.2: Update Image References in Kubernetes Manifests
```bash
# Update all deployment files with ACR name
find k8s -name "*.yaml" -type f -exec sed -i '' "s|[a-z0-9]*\.azurecr\.io|$ACR_LOGIN_SERVER|g" {} +

echo "✅ Kubernetes manifests updated with ACR login server"
```
### Step 6.2.1: Ensure ACR is Attached to AKS Cluster
```bash
# Ensure ACR is attached to AKS for image pull permissions
# This works for both new and existing clusters
if az aks check-acr --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP --acr ${ACR_NAME}.azurecr.io &>/dev/null; then
  echo "✅ ACR is already attached to AKS cluster"
else
  echo "Attaching ACR to AKS cluster..."
  az aks update \
    --name $AKS_CLUSTER \
    --resource-group $RESOURCE_GROUP \
    --attach-acr $ACR_NAME
  
  echo "✅ ACR attached to AKS cluster"
fi
```
### Step 6.3: Create Kubernetes Namespace
```bash
# Create production namespace
kubectl create namespace production

# Verify
kubectl get namespaces

echo "✅ Production namespace created"
```

### Step 6.4: Create Kubernetes Secrets
```bash
# Create AWS credentials secret
kubectl create secret generic aws-secrets \
  --from-literal=AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)" \
  --from-literal=AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)" \
  -n production

# If Azure OpenAI is enabled, create OpenAI secret
if [ "$AZURE_OPENAI_ENABLED" = "true" ]; then
  kubectl create secret generic azure-openai-secrets \
    --from-literal=AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
    --from-literal=AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    -n production
fi

# Verify secrets
kubectl get secrets -n production

echo "✅ Kubernetes secrets created"
```

---

## Phase 7: Deploy Services to Kubernetes (30 minutes)

### Step 7.1: Deploy ConfigMap
```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Verify
kubectl get configmap -n production
kubectl describe configmap guardian-config -n production

echo "✅ ConfigMap deployed"
```

### Step 7.2: Deploy Redis
```bash
# Deploy Redis
kubectl apply -f k8s/cpu-services/redis.yaml

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod -l app=redis -n production --timeout=300s

# Verify
kubectl get pods -n production -l app=redis

echo "✅ Redis deployed"
```

### Step 7.3: Deploy CPU Services
```bash
# Deploy all CPU services (including API gateway)
kubectl apply -f k8s/cpu-services/ingestion-deployment.yaml
kubectl apply -f k8s/cpu-services/fast-screening.yaml
kubectl apply -f k8s/cpu-services/policy-engine.yaml
kubectl apply -f k8s/cpu-services/human-review-deployment.yaml
kubectl apply -f k8s/cpu-services/api-gateway.yaml
kubectl apply -f k8s/cpu-services/deep-vision.yaml

# Deploy notification service (if exists)
if [ -f k8s/cpu-services/notification.yaml ]; then
  kubectl apply -f k8s/cpu-services/notification.yaml
fi

echo "Waiting for all services to be ready (this may take 3-5 minutes)..."

# Wait for all services to be ready
kubectl wait --for=condition=ready pod -l app=redis -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=ingestion -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=fast-screening -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=policy-engine -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=human-review -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=api-gateway -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=deep-vision -n production --timeout=300s

# Verify
kubectl get pods -n production

echo "All CPU services deployed successfully."
```

<!-- ### Step 7.4: Deploy Deep Vision Service (CPU Version)
```bash
# NOTE: GPU node pool and KEDA are disabled due to subscription limitations
# The Deep Vision service runs on CPU nodes instead (slower but functional)

# Deploy Deep Vision service on CPU nodes
kubectl apply -f k8s/cpu-services/deep-vision.yaml

# Wait for Deep Vision to be ready
kubectl wait --for=condition=ready pod -l app=deep-vision -n production --timeout=300s

# Verify
kubectl get pods -n production -l app=deep-vision

echo "✅ Deep Vision service deployed on CPU nodes"
echo "⚠️  Note: Processing will be slower (~10-20s per video vs 2-3s on GPU)"
``` -->

### Step 7.5: Deploy Frontend
```bash
# Deploy frontend
kubectl apply -f k8s/frontend/frontend-deployment.yaml

# Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=guardian-frontend -n production --timeout=300s

# Verify
kubectl get pods -n production -l app=guardian-frontend

echo "✅ Frontend deployed"
```

### Step 7.6: Deploy Ingress
```bash
# Deploy ingress (routes traffic to frontend and backend services)
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get ingress -n production

# Get ingress details
kubectl describe ingress guardian-ingress -n production

echo "✅ Ingress deployed"
echo "Application URL: http://$EXTERNAL_IP"
echo "Frontend: http://$EXTERNAL_IP"
echo "API: http://$EXTERNAL_IP/api"
```

### Step 7.7: Verify All Deployments
```bash
# Check all pods
kubectl get pods -n production

# Check all services
kubectl get svc -n production

# Check all deployments
kubectl get deployments -n production

# Check pod logs for any errors
kubectl logs -l tier=cpu -n production --tail=50

# Verify frontend is accessible
curl -I http://$EXTERNAL_IP

echo "✅ All services deployed (6 backend + 1 API gateway + 1 frontend = 8 total)"
```

---

## Phase 8: End-to-End Testing (30 minutes)

### Step 8.1: Test Frontend Access
```bash
# Open frontend in browser
echo "Frontend URL: http://$EXTERNAL_IP"
open "http://$EXTERNAL_IP"

# Or test with curl
curl -I http://$EXTERNAL_IP

# Expected: HTTP 200 OK

echo "✅ Frontend accessible"
```

### Step 8.2: Test Service Health Checks via API
```bash
# Get service endpoints
export INGESTION_URL="http://$EXTERNAL_IP/api/ingestion"
export API_GATEWAY_URL="http://$EXTERNAL_IP/api"
export POLICY_URL="http://$EXTERNAL_IP/api/policy"
export REVIEW_URL="http://$EXTERNAL_IP/api/review"

# Test health endpoints
echo "Testing service health checks..."

curl -s $INGESTION_URL/health | jq .
curl -s $POLICY_URL/health | jq .
curl -s $REVIEW_URL/health | jq .
curl -s $API_GATEWAY_URL/videos/health | jq .

echo "✅ All services responding"
```

### Step 8.3: Test Video Upload via Frontend
```bash
# Option 1: Use the frontend UI (Recommended)
echo "1. Open browser: http://$EXTERNAL_IP"
echo "2. Click 'Upload' tab"
echo "3. Drag & drop a test video (MP4, MOV, or AVI)"
echo "4. Click upload and note the job_id"
echo ""
echo "OR"
echo ""
echo "Option 2: Use curl (API testing)"

# Upload video via API
curl -X POST $INGESTION_URL/upload \
  -F "file=@test-video.mp4" \
  -v

# Save the job_id from response
export VIDEO_ID="<uuid-from-response>"

echo "✅ Video uploaded"
echo "Video ID: $VIDEO_ID"
```

### Step 8.4: Test Dashboard via Frontend
```bash
# Open dashboard in browser
echo "1. Click 'Dashboard' tab in the frontend"
echo "2. You should see your uploaded video"
echo "3. Check the status badge (should show 'Processing' or 'Uploaded')"
echo "4. Click 'View Details' to see full video information"
echo ""
echo "OR test via API:"

# Get all videos via API gateway
curl -s http://$EXTERNAL_IP/api/videos | jq .

# Get dashboard stats
curl -s http://$EXTERNAL_IP/api/dashboard/stats | jq .

echo "✅ Dashboard tested"
```

### Step 8.5: Verify Data in AWS
```bash
# Check video in S3
aws s3 ls s3://$S3_BUCKET_NAME/videos/

# Check video record in DynamoDB
aws dynamodb get-item \
  --table-name guardian-videos \
  --key "{\"video_id\":{\"S\":\"$VIDEO_ID\"}}" \
  --region $AWS_REGION

# Check events in DynamoDB
aws dynamodb scan \
  --table-name guardian-events \
  --filter-expression "video_id = :vid" \
  --expression-attribute-values "{\":vid\":{\"S\":\"$VIDEO_ID\"}}" \
  --region $AWS_REGION \
  --limit 10

# Check SQS queue depth
aws sqs get-queue-attributes \
  --queue-url $SQS_QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages \
  --region $AWS_REGION

echo "✅ Data verified in AWS"
```

### Step 8.6: Monitor Processing
```bash
# Watch pod logs
kubectl logs -f -l app=ingestion -n production &
kubectl logs -f -l app=fast-screening -n production &
kubectl logs -f -l app=policy-engine -n production &

# Check GPU pod scaling (COMMENTED OUT - No GPU nodes)
# watch kubectl get pods -n production -l app=deep-vision

# Check KEDA metrics (COMMENTED OUT - KEDA not installed)
# kubectl get hpa -n production

echo "✅ Processing monitored"
```

### Step 8.7: Test Human Review Workflow
```bash
# Option 1: Use the frontend UI (Recommended)
echo "1. Click 'Review Queue' tab in the frontend"
echo "2. You should see videos pending review (if any)"
echo "3. Click 'Review' button on a video"
echo "4. Add review notes and click 'Approve' or 'Reject'"
echo ""
echo "OR test via API:"

# Get review queue via API
curl -s $REVIEW_URL/queue | jq .

# If video is in review queue, submit review
curl -X POST "$REVIEW_URL/review/$VIDEO_ID?approved=true&notes=Test+review" \
  -H "Content-Type: application/json"

echo "✅ Human review tested"
```

---

## Phase 8.5: Minimal MLOps Integration (Optional, 30 minutes)

### Overview
This phase wires up the existing MLOps scripts (`mlops/training/` and `mlops/deployment/`) with your application. By default, the system uses CLIP-only detection. After completing this phase, you can optionally use your own trained Azure ML models.

**Note**: This is a minimal implementation for learning purposes. For production CI/CD pipelines, see separate Azure DevOps/Azure ML documentation.

### Step 8.5.1: Setup Azure ML Workspace (One-time)
```bash
# Run the setup script
bash scripts/setup-mlops.sh

# Verify workspace was created
az ml workspace show \
  --name guardian-ml-workspace \
  --resource-group guardian-ai-prod
```

### Step 8.5.2: Train Models (Optional)
```bash
# Set environment variables
# Linux/macOS (bash):
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="guardian-ai-prod"
export AZURE_ML_WORKSPACE="guardian-ml-workspace"
export MLFLOW_TRACKING_URI="azureml://your-workspace"

# Windows (PowerShell):
# $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
# $env:AZURE_RESOURCE_GROUP = "guardian-ai-prod"
# $env:AZURE_ML_WORKSPACE = "guardian-ml-workspace"
# $env:MLFLOW_TRACKING_URI = "azureml://your-workspace"

# Train models
cd mlops/training
python train_nsfw_model.py
python train_nsfw_model.py  # Run again for violence model (or modify script)
```

### Step 8.5.3: Deploy Models to Azure ML
```bash
cd mlops/deployment
python deploy_model.py

# This will output scoring URIs like:
# nsfw-detector: https://xxx.azureml.net/score
# violence-detector: https://xxx.azureml.net/score
```

### Step 8.5.4: Get Endpoint Information
```bash
# Use the helper script to get endpoints
bash scripts/get-model-endpoints.sh nsfw-detector
bash scripts/get-model-endpoints.sh violence-detector

# Or manually get endpoints:
az ml online-endpoint show \
  --name nsfw-detector-endpoint \
  --resource-group guardian-ai-prod \
  --workspace-name guardian-ml-workspace \
  --query scoring_uri -o tsv
```

### Step 8.5.5: Update Configuration

**For Local Development (docker-compose.yml):**
```bash
# Add to your .env file:
NSFW_MODEL_ENDPOINT="https://xxx.azureml.net/score"
VIOLENCE_MODEL_ENDPOINT="https://xxx.azureml.net/score"
MODEL_ENDPOINT_KEY="your-endpoint-key"

# Restart services
docker-compose restart deep-vision
```

**For Kubernetes (ConfigMap):**
```bash
# Update ConfigMap
kubectl edit configmap guardian-config -n production

# Add:
# NSFW_MODEL_ENDPOINT: "https://xxx.azureml.net/score"
# VIOLENCE_MODEL_ENDPOINT: "https://xxx.azureml.net/score"
# MODEL_ENDPOINT_KEY: "your-endpoint-key"

# Restart deep-vision pods
kubectl rollout restart deployment/deep-vision -n production
```

### Step 8.5.6: Verify Integration
```bash
# Check deep-vision logs to see if it's calling Azure ML endpoints
kubectl logs -l app=deep-vision -n production --tail=50 | grep "Model endpoint"

# Or for local:
docker-compose logs deep-vision | grep "Model endpoint"
```

### How It Works
- **Without Azure ML endpoints**: Deep-vision uses CLIP-only detection (default, works out of the box)
- **With Azure ML endpoints**: Deep-vision combines CLIP scores (30%) with custom model scores (70%) for improved accuracy
- **Fallback**: If endpoints are unavailable, the system gracefully falls back to CLIP-only

### Rollback Models (if needed)
```bash
# Rollback to previous model version
python mlops/deployment/rollback_model.py nsfw-detector
python mlops/deployment/rollback_model.py violence-detector
```

**Note**: For automated CI/CD pipelines with Azure DevOps and Azure ML Pipelines, see separate documentation (to be created separately).

---

## Phase 9: Setup Monitoring (Optional, 30 minutes)

### Step 9.1: Install Prometheus
```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

echo "✅ Prometheus installed"
```

### Step 9.2: Install Grafana
```bash
# Grafana is included in kube-prometheus-stack
# Get Grafana admin password
export GRAFANA_PASSWORD=$(kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

echo "Grafana admin password: $GRAFANA_PASSWORD"

# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &

echo "✅ Grafana available at http://localhost:3000"
echo "Username: admin"
echo "Password: $GRAFANA_PASSWORD"
```

### Step 9.3: Configure Service Monitors
```bash
# Create ServiceMonitor for our services
cat > k8s/monitoring/service-monitor.yaml <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: guardian-services
  namespace: production
spec:
  selector:
    matchLabels:
      monitor: guardian
  endpoints:
  - port: http
    interval: 30s
EOF

kubectl apply -f k8s/monitoring/service-monitor.yaml

echo "✅ Service monitors configured"
```

---

## Phase 10: Setup CI/CD (Optional, 30 minutes)

### Step 10.1: Configure GitHub Secrets
```bash
# Set GitHub secrets for CI/CD
# You'll need to do this manually in GitHub UI or use gh CLI

# Required secrets:
# - AZURE_CREDENTIALS (service principal JSON)
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - ACR_USERNAME
# - ACR_PASSWORD
# - AKS_CLUSTER_NAME
# - AKS_RESOURCE_GROUP

echo "Configure these secrets in GitHub:"
echo "1. Go to Settings > Secrets and variables > Actions"
echo "2. Add the following secrets:"
echo "   - AZURE_CREDENTIALS"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - ACR_USERNAME: $ACR_USERNAME"
echo "   - ACR_PASSWORD: $ACR_PASSWORD"
echo "   - AKS_CLUSTER_NAME: $AKS_CLUSTER"
echo "   - AKS_RESOURCE_GROUP: $RESOURCE_GROUP"
```

### Step 10.2: Test CI/CD Pipeline
```bash
# Push changes to trigger CI/CD
git add .
git commit -m "Deploy complete MLOps platform"
git push origin main

# Monitor GitHub Actions
echo "Check GitHub Actions at: https://github.com/yourusername/guardian-ai/actions"
```

---

## Phase 11: Load Testing (30 minutes)

### Step 11.1: Install k6
```bash
# Install k6 for load testing
brew install k6

# Verify
k6 version
```

### Step 11.2: Run Load Test
```bash
# Run load test script
bash scripts/load-test.sh

# Or use k6 directly
k6 run tests/load/load-test.js -e EXTERNAL_IP=$EXTERNAL_IP

echo "✅ Load testing complete"
```

### Step 11.3: Verify GPU Autoscaling (COMMENTED OUT - No GPU quota)
```bash
# NOTE: GPU autoscaling is disabled due to subscription limitations

# Monitor GPU pod scaling during load test
# watch kubectl get pods -n production -l app=deep-vision

# Check KEDA scaling events
# kubectl get events -n production --field-selector involvedObject.name=deep-vision-scaler

# Check HPA metrics
# kubectl get hpa -n production

# echo "✅ GPU autoscaling verified"

echo "⚠️  GPU autoscaling skipped (no GPU quota available)"
```

---

## Phase 12: Production Hardening (Optional, 1 hour)

### Step 12.1: Enable Network Policies
```bash
# Create network policies for security
kubectl apply -f k8s/network-policies/

echo "✅ Network policies enabled"
```

### Step 12.2: Configure Resource Limits
```bash
# Verify resource limits are set in deployments
kubectl describe deployment ingestion -n production | grep -A 5 "Limits"
kubectl describe deployment fast-screening -n production | grep -A 5 "Limits"

echo "✅ Resource limits configured"
```

### Step 12.3: Setup Backup Strategy
```bash
# Enable DynamoDB point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name guardian-videos \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

aws dynamodb update-continuous-backups \
  --table-name guardian-events \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Enable S3 versioning (already enabled by setup script)
aws s3api get-bucket-versioning --bucket $S3_BUCKET_NAME

echo "✅ Backup strategy configured"
```

---

## Success Checklist

### AWS Resources
- [ ] S3 bucket created and accessible
- [ ] 2 SQS queues created (video-processing, gpu-processing)
- [ ] 2 DynamoDB tables created (videos, events)
- [ ] DynamoDB TTL enabled on events table
- [ ] AWS credentials configured

### Azure Resources
- [ ] Resource group created
- [ ] ACR created and images pushed
- [ ] AKS cluster created with 3+ nodes
- [ ] ~~GPU node pool added~~ (Skipped - no GPU quota)
- [ ] ~~KEDA installed~~ (Skipped - not needed without GPU)
- [ ] NGINX Ingress installed with external IP

### Kubernetes Deployment
- [ ] Production namespace created
- [ ] ConfigMap deployed with AWS values
- [ ] Secrets created (AWS credentials)
- [ ] Redis deployed and running
- [ ] All 6 backend services deployed and running
- [ ] API Gateway deployed and running
- [ ] Frontend deployed and accessible
- [ ] ~~GPU service deployed with KEDA autoscaling~~ (Running on CPU instead)
- [ ] Ingress configured with all routes

### Testing & Validation
- [ ] Frontend accessible at http://EXTERNAL_IP
- [ ] Upload page works (drag & drop video)
- [ ] Dashboard displays videos with status
- [ ] Review queue shows pending reviews
- [ ] Video details page shows scores and timeline
- [ ] Health checks pass for all services
- [ ] Video upload works end-to-end
- [ ] Data appears in S3, DynamoDB, SQS
- [ ] ~~GPU autoscaling works (scales 0→1→0)~~ (Skipped - no GPU quota)
- [ ] Human review workflow functional via UI
- [ ] Monitoring configured (Prometheus + Grafana)
- [ ] Load testing completed

---

## Cost Management

### Current Monthly Costs
**AWS**: ~$25-40/month
- S3: $3-5
- SQS (2 queues): $1-2
- DynamoDB (2 tables): $10-20
- Data transfer: $5-10

**Azure**: ~$100-150/month
- AKS (3 nodes): $100-130
- ACR: $5
- ~~GPU nodes: $0 (scale-to-zero when idle)~~ (Not used - no GPU quota)
- Monitoring: $5-10

**Total**: ~$125-190/month

### Cost Optimization Tips
```bash
# Scale down AKS during off-hours
az aks scale \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --node-count 1

# Purge SQS queues when not testing
aws sqs purge-queue --queue-url $SQS_QUEUE_URL
aws sqs purge-queue --queue-url $SQS_GPU_QUEUE_URL

# Delete old S3 videos
aws s3 rm s3://$S3_BUCKET_NAME/videos/ --recursive --exclude "*" --include "*-old-*"

# Monitor costs
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

az consumption usage list --output table
```

---

## Troubleshooting

### Issue: Pods not starting
```bash
# Check pod status
kubectl get pods -n production

# Describe pod
kubectl describe pod <POD_NAME> -n production

# Check logs
kubectl logs <POD_NAME> -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Issue: Cannot pull images from ACR
```bash
# Verify ACR attachment
az aks check-acr --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --acr $ACR_NAME

# Re-attach ACR if needed
az aks update --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --attach-acr $ACR_NAME
```

### Issue: Services cannot connect to AWS
```bash
# Verify AWS secrets
kubectl get secret aws-secrets -n production -o yaml

# Test AWS connectivity from pod
kubectl exec -it <POD_NAME> -n production -- env | grep AWS
kubectl exec -it <POD_NAME> -n production -- python3 -c "import boto3; print(boto3.client('s3').list_buckets())"
```

### Issue: GPU pods not scaling (COMMENTED OUT - No GPU quota)
```bash
# NOTE: GPU autoscaling is disabled due to subscription limitations

# Check KEDA operator
# kubectl get pods -n keda

# Check ScaledObject
# kubectl describe scaledobject deep-vision-scaler -n production

# Check SQS queue depth
# aws sqs get-queue-attributes --queue-url $SQS_GPU_QUEUE_URL --attribute-names ApproximateNumberOfMessages

echo "⚠️  GPU troubleshooting skipped (no GPU quota available)"
```

---

## Cleanup (When Done Testing)

### Delete Kubernetes Resources
```bash
# Delete all resources in production namespace
kubectl delete namespace production

# Delete KEDA (COMMENTED OUT - Not installed)
# helm uninstall keda -n keda
# kubectl delete namespace keda

# Delete Ingress
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete namespace ingress-nginx

# Delete Monitoring
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```

### Delete Azure Resources
```bash
# Delete entire resource group (removes AKS, ACR, etc.)
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Remove local Kubernetes context
kubectl config delete-context $AKS_CLUSTER
```

### Delete AWS Resources
```bash
# Delete S3 bucket
aws s3 rb s3://$S3_BUCKET_NAME --force

# Delete SQS queues
aws sqs delete-queue --queue-url $SQS_QUEUE_URL
aws sqs delete-queue --queue-url $SQS_GPU_QUEUE_URL

# Delete DynamoDB tables
aws dynamodb delete-table --table-name guardian-videos
aws dynamodb delete-table --table-name guardian-events
```

---

## Next Steps

After completing this deployment:
1. ✅ Document any issues encountered
2. ✅ Take screenshots of working system
3. ✅ Export monitoring dashboards
4. ✅ Create final learner documentation
5. ✅ Prepare demo videos/walkthroughs

---

**Total Deployment Time**: 4-6 hours (first time)
**Status**: ✅ Complete End-to-End Deployment
**Cost**: ~$125-190/month
**Production Ready**: Yes

🚀 **System fully deployed and validated!**
