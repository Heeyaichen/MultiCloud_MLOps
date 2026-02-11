# Guardian AI - MLOps Project

**End-to-End MLOps Pipeline for ML Model Training and Deployment on Azure**

A production-ready MLOps project demonstrating automated machine learning workflows using Azure Machine Learning, Azure DevOps, and MLflow. This project implements a complete lifecycle from model training on compute clusters to automated deployment to online endpoints.

---

## 🎯 Project Overview

This project provides a complete MLOps implementation featuring:

- **Automated Model Training** - Azure ML compute cluster-based training with MLflow tracking
- **Model Registry** - Centralized model versioning and management in Azure ML
- **CI/CD Pipelines** - Azure DevOps pipelines for training and deployment automation
- **Online Endpoint Deployment** - Automated deployment to Azure ML managed endpoints
- **Multi-Model Support** - Training and deployment pipelines for multiple models (NSFW and Violence detection)

---

## 🏗️ Architecture

### Multi-Cloud Architecture

This project implements a hybrid cloud architecture leveraging both AWS and Azure services:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Application Layer                            │
│  (Microservices: Ingestion, Fast-Screening, Deep-Vision, etc.)      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼───────┐   ┌───────▼───────┐
            │   AWS Cloud   │   │  Azure Cloud   │
            └───────┬───────┘   └───────┬───────┘
                    │                   │
        ┌───────────┼───────────┐       │
        │           │           │       │
    ┌───▼───┐  ┌───▼───┐  ┌───▼───┐     │
    │  S3   │  │  SQS  │  │DynamoDB│    │
    │Storage│  │Queues │  │Database│    │
    └───────┘  └───────┘  └────────┘    │
                                        │
                     ┌──────────────────┼──────────────────┐
                     │                  │                  │
             ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
             │  Azure ML     │  │ Azure DevOps  │  │  Azure ML     │
             │  Workspace    │  │   Pipelines   │  │  Endpoints    │
             │               │  │               │  │               │
             │ • Compute     │  │ • Training    │  │ • NSFW Model  │
             │   Clusters    │  │ • Deployment  │  │ • Violence    │
             │ • Model       │  │               │  │   Model       │
             │   Registry    │  │               │  │               │
             │ • MLflow      │  │               │  │               │
             └───────────────┘  └───────────────┘  └───────────────┘
```

### Service Integration Flow

1. **Data Storage & Messaging (AWS)** → Application services store videos and process messages
2. **Model Training (Azure)** → Azure ML trains models on compute clusters
3. **Model Deployment (Azure)** → Models deployed to Azure ML online endpoints
4. **Model Integration** → Application services call Azure ML endpoints for inference
5. **CI/CD (Azure DevOps)** → Automated pipelines orchestrate the entire workflow

### MLOps Workflow

1. **Code Commit** → Push to Azure DevOps repository
2. **Training Pipeline** → Submits jobs to Azure ML compute cluster
3. **Model Training** → Executes on compute cluster with MLflow tracking
4. **Model Registration** → Automatically registers models in Azure ML Model Registry
5. **Deployment Pipeline** → Deploys registered models to online endpoints
6. **Endpoint Management** → Updates Kubernetes ConfigMaps with endpoint URLs
7. **Application Integration** → Application services use Azure ML endpoints for inference

---

## ☁️ Cloud Services & Resources

### AWS Services

| Service | Purpose | Usage in Project |
|---------|---------|------------------|
| **S3 (Simple Storage Service)** | Object storage for video files | Primary storage for uploaded videos. Application services upload/download videos from S3 buckets. |
| **SQS (Simple Queue Service)** | Message queuing for asynchronous processing | Two queues: `video-processing` (main queue) and `gpu-processing` (high-risk videos). Enables decoupled, scalable processing. |
| **DynamoDB** | NoSQL database for metadata and events | Two tables: `guardian-videos` (video metadata, status, risk scores) and `guardian-events` (audit log with TTL). Single source of truth for application state. |

**AWS Integration Points:**
- **Ingestion Service** → Uploads videos to S3, creates DynamoDB records
- **Fast-Screening Service** → Reads from SQS, updates DynamoDB with risk scores
- **Deep-Vision Service** → Downloads videos from S3, processes, updates DynamoDB
- **Policy Engine** → Reads/writes video decisions to DynamoDB
- **API Gateway** → Queries DynamoDB for video listings and status

### Azure Services

| Service | Purpose | Usage in Project |
|---------|---------|------------------|
| **Azure ML Workspace** | Centralized ML platform | Manages compute clusters, model registry, MLflow tracking, and online endpoints. Core MLOps infrastructure. |
| **Azure ML Compute Clusters** | Scalable compute for training | CPU-based clusters (`cpu-training-cluster`) execute training jobs. Auto-scales based on workload. |
| **Azure ML Model Registry** | Model versioning and management | Stores trained models (`nsfw-detector`, `violence-detector`) with versioning, metadata, and lineage tracking. |
| **Azure ML Online Endpoints** | Real-time inference endpoints | Managed endpoints (`nsfw-detector-endpoint`, `violence-detector-endpoint`) serve model predictions via REST API. |
| **Azure DevOps** | CI/CD and pipeline orchestration | Hosts training and deployment pipelines. Manages code repository, variable groups, and service connections. |
| **Azure Container Registry (ACR)** | Container image storage | Stores Docker images for application services (used in Kubernetes deployments). |
| **Azure Kubernetes Service (AKS)** | Container orchestration | Hosts application microservices and integrates with Azure ML endpoints via ConfigMaps. |
| **Azure OpenAI** | LLM services (Optional) | Provides GPT-4o for human review copilot and policy interpretation. Disabled by default. |

**Azure Integration Points:**
- **Training Pipeline** → Submits jobs to Azure ML compute clusters
- **Deployment Pipeline** → Deploys models from registry to online endpoints
- **Deep-Vision Service** → Calls Azure ML endpoints (`NSFW_MODEL_ENDPOINT`, `VIOLENCE_MODEL_ENDPOINT`) for inference
- **Kubernetes ConfigMap** → Stores Azure ML endpoint URLs and keys for application services
- **Azure DevOps** → Orchestrates entire MLOps workflow

### Service Relationships & Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Data Flow                         │
└─────────────────────────────────────────────────────────────────┘

1. Video Upload
   └─> Ingestion Service → S3 (store video) + DynamoDB (create record)
   
2. Video Processing
   └─> SQS Queue → Fast-Screening Service → DynamoDB (update risk_score)
   
3. High-Risk Processing
   └─> SQS GPU Queue → Deep-Vision Service → Azure ML Endpoints (inference)
       └─> DynamoDB (update with model predictions)
       
4. Decision Making
   └─> Policy Engine → DynamoDB (read scores) → Decision → DynamoDB (write decision)
   
5. Human Review (if needed)
   └─> Human-Review Service → DynamoDB (read/write review status)
   
6. Notifications
   └─> Notification Service → DynamoDB Events Table (audit log)

┌─────────────────────────────────────────────────────────────────┐
│                    MLOps Pipeline Flow                           │
└─────────────────────────────────────────────────────────────────┘

1. Code Commit
   └─> Azure DevOps Repository
   
2. Training Pipeline Trigger
   └─> Azure DevOps Pipeline → Azure ML Compute Cluster
       └─> Training Scripts → MLflow Tracking → Model Artifacts
       
3. Model Registration
   └─> Azure ML Model Registry (automatic after training)
   
4. Deployment Pipeline Trigger
   └─> Azure DevOps Pipeline → Azure ML Online Endpoints
       └─> Model from Registry → Endpoint Deployment
       
5. Endpoint Integration
   └─> Kubernetes ConfigMap Update → Application Services
       └─> Deep-Vision Service uses endpoints for inference
```

### Cross-Cloud Integration

**How AWS and Azure Work Together:**

1. **Data Layer (AWS)**:
   - Videos stored in S3
   - Metadata and events in DynamoDB
   - Message queues in SQS

2. **ML Layer (Azure)**:
   - Models trained on Azure ML compute clusters
   - Models registered in Azure ML Model Registry
   - Models deployed to Azure ML online endpoints

3. **Integration Point**:
   - Application services (running on Azure Kubernetes or locally) use AWS for data
   - Application services call Azure ML endpoints for model inference
   - Azure DevOps pipelines orchestrate model training and deployment
   - Kubernetes ConfigMaps bridge Azure ML endpoints to application services

**Benefits of Multi-Cloud Approach:**
- **Cost Optimization**: AWS for storage/queues (lower cost), Azure for ML (better ML tools)
- **Best-of-Breed**: Use each cloud's strengths
- **Scalability**: Independent scaling of data and ML infrastructure
- **Flexibility**: Can migrate components between clouds if needed

---

## 📋 Prerequisites

### Required Accounts & Services

**AWS Account:**
- AWS account with IAM credentials
- S3 bucket for video storage
- SQS queues (`video-processing`, `gpu-processing`)
- DynamoDB tables (`guardian-videos`, `guardian-events`)

**Azure Subscription:**
- Azure subscription with active subscription ID
- Azure DevOps organization and project
- Azure ML Workspace (`guardian-ai-ml-workspace-prod`)
- Azure Resource Group (`guardian-ai-prod`)
- Azure ML Compute Cluster (`cpu-training-cluster`)
- Azure Container Registry (ACR) - for Kubernetes deployments
- Azure Kubernetes Service (AKS) - optional, for production deployment

### Local Development Tools

```bash
# Required
- Python 3.8+
- Azure CLI 2.50+
- AWS CLI 2.13+
- Git

# Optional
- Docker Desktop (for local testing)
- kubectl (for Kubernetes integration)
- Azure DevOps CLI
```

### AWS Setup

1. **Create AWS Resources**:
   ```bash
   # Run setup script
   bash scripts/setup-aws.sh
   
   # This creates:
   # - S3 bucket: guardian-videos-<account-id>
   # - SQS queues: guardian-video-processing, guardian-gpu-processing
   # - DynamoDB tables: guardian-videos, guardian-events
   ```

2. **Configure AWS Credentials**:
   ```bash
   aws configure
   # Enter AWS Access Key ID, Secret Access Key, Region
   ```

3. **Get Resource Names**:
   ```bash
   export S3_BUCKET_NAME="guardian-videos-$(aws sts get-caller-identity --query Account --output text | cut -c1-8)"
   export SQS_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-video-processing --query 'QueueUrl' --output text)
   export SQS_GPU_QUEUE_URL=$(aws sqs get-queue-url --queue-name guardian-gpu-processing --query 'QueueUrl' --output text)
   ```

### Azure DevOps Setup

1. **Variable Group**: Create `guardian-variables` with:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP` = `guardian-ai-prod`
   - `AZURE_ML_WORKSPACE` = `guardian-ai-ml-workspace-prod`
   - `AZURE_ML_REGION` = `eastus`
   - `COMPUTE_CLUSTER` = `cpu-training-cluster`

2. **Service Connection**: Create Azure Resource Manager service connection (`guardian-azure-connection`)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd MLOps_Project
```

### 2. Setup AWS Resources

```bash
# Configure AWS CLI
aws configure

# Create AWS resources (S3, SQS, DynamoDB)
bash scripts/setup-aws.sh

# Verify resources created
aws s3 ls | grep guardian-videos
aws sqs list-queues | grep guardian
aws dynamodb list-tables | grep guardian
```

### 3. Setup Azure ML Workspace

```bash
# Login to Azure
az login

# Set environment variables
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="guardian-ai-prod"
export AZURE_ML_WORKSPACE="guardian-ai-ml-workspace-prod"
export AZURE_ML_REGION="eastus"

# Create compute cluster (if not exists)
az ml compute create \
  --name cpu-training-cluster \
  --type amlcompute \
  --min-instances 0 \
  --max-instances 4 \
  --vm-size Standard_DS3_v2 \
  --workspace-name $AZURE_ML_WORKSPACE \
  --resource-group $AZURE_RESOURCE_GROUP
```

### 4. Configure Azure DevOps

1. Push code to Azure DevOps repository
2. Create variable group `guardian-variables` with required variables
3. Create service connection `guardian-azure-connection`
4. Import pipelines:
   - `azure-pipelines-ml-training.yml`
   - `azure-pipelines-ml-deployment.yml`

### 5. Run Training Pipeline

1. Go to Azure DevOps → Pipelines
2. Select `azure-pipelines-ml-training.yml`
3. Click **Run pipeline**
4. Monitor job execution in Azure ML Studio

### 6. Deploy Models

After training completes and models are registered:

1. Go to Azure DevOps → Pipelines
2. Select `azure-pipelines-ml-deployment.yml`
3. Click **Run pipeline**
4. Verify endpoints in Azure ML Studio → Endpoints

### 7. Integrate Endpoints with Application

After deployment, endpoints are automatically integrated:

- **Kubernetes**: ConfigMap updated with endpoint URLs
- **Local Development**: Set environment variables:
  ```bash
  export NSFW_MODEL_ENDPOINT="https://nsfw-detector-endpoint.eastus.inference.ml.azure.com/score"
  export VIOLENCE_MODEL_ENDPOINT="https://violence-detector-endpoint.eastus.inference.ml.azure.com/score"
  export MODEL_ENDPOINT_KEY="your-endpoint-key"
  ```

---

## 📁 Project Structure

```
MLOps_Project/
├── mlops/
│   ├── training/
│   │   ├── train_nsfw_model.py          # NSFW model training script
│   │   ├── train_violence_model.py      # Violence model training script
│   │   └── submit_training_job.py       # Job submission orchestrator
│   └── deployment/
│       ├── deploy_model.py               # Model deployment script
│       └── rollback_model.py             # Model rollback utility
├── azure-pipelines-ml-training.yml      # Training CI/CD pipeline
├── azure-pipelines-ml-deployment.yml    # Deployment CI/CD pipeline
├── docs/
│   ├── COMPUTE_CLUSTER_WORKFLOW.md      # Complete workflow guide
│   └── AZURE_DEVOPS_ML_INTEGRATION_GUIDE.md
└── scripts/
    ├── get-model-endpoints.sh            # Endpoint retrieval script
    └── update-model-endpoints-in-k8s.sh # Kubernetes integration
```

---

## 🔄 MLOps Workflow

### Training Pipeline (`azure-pipelines-ml-training.yml`)

**What it does:**
- Submits training jobs to Azure ML compute cluster
- Supports multiple model types (NSFW, Violence)
- Automatically registers models in Azure ML Model Registry
- Tracks training metrics with MLflow

**Pipeline Steps:**
1. Setup Python environment
2. Install Azure ML SDK dependencies
3. Azure CLI authentication
4. Submit NSFW training job to compute cluster
5. Submit Violence training job to compute cluster
6. Monitor job completion

**Output:**
- Registered models in Azure ML Model Registry
- MLflow experiment runs with metrics
- Model artifacts stored in Azure ML workspace

### Deployment Pipeline (`azure-pipelines-ml-deployment.yml`)

**What it does:**
- Deploys registered models to Azure ML online endpoints
- Creates managed endpoints with health probes
- Updates Kubernetes ConfigMaps with endpoint URLs
- Restarts application pods to use new endpoints

**Pipeline Steps:**
1. Install deployment dependencies
2. Azure CLI authentication
3. Deploy models to online endpoints
4. Retrieve endpoint information
5. Update Kubernetes ConfigMap
6. Restart application deployments

**Output:**
- Online endpoints (`nsfw-detector-endpoint`, `violence-detector-endpoint`)
- Scoring URIs for inference
- Updated Kubernetes configuration

---

## 🧪 Model Training

### Training Scripts

**NSFW Detection Model** (`train_nsfw_model.py`)
- PyTorch-based image classification model
- ResNet50 backbone
- MLflow tracking integration
- Automatic model registration

**Violence Detection Model** (`train_violence_model.py`)
- Similar architecture to NSFW model
- Separate training pipeline
- Independent model registration

### Training Configuration

- **Framework**: PyTorch
- **Compute**: Azure ML CPU compute cluster
- **Tracking**: MLflow with Azure ML backend
- **Registry**: Azure ML Model Registry
- **Environment**: Curated PyTorch environment or custom

### Running Training Locally (Optional)

```bash
cd mlops/training

# Set environment variables
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="guardian-ai-prod"
export AZURE_ML_WORKSPACE="guardian-ai-ml-workspace-prod"
export AZURE_ML_REGION="eastus"
export COMPUTE_CLUSTER="cpu-training-cluster"

# Submit training job
python submit_training_job.py \
  --model-type nsfw \
  --subscription-id $AZURE_SUBSCRIPTION_ID \
  --resource-group $AZURE_RESOURCE_GROUP \
  --workspace-name $AZURE_ML_WORKSPACE \
  --compute-cluster $COMPUTE_CLUSTER
```

---

## 🚢 Model Deployment

### Deployment Process

1. **Retrieve Latest Model**: Gets latest version from Model Registry
2. **Create Endpoint**: Creates or updates Azure ML online endpoint
3. **Deploy Model**: Deploys model with health probes and scaling
4. **Traffic Management**: Configures traffic split (champion/challenger)
5. **Integration**: Updates Kubernetes ConfigMap with endpoint URLs

### Endpoint Configuration

- **Instance Type**: `Standard_DS3_v2`
- **Instance Count**: 3 (champion), 1 (challenger if A/B testing enabled)
- **Health Probes**: Liveness and readiness probes configured
- **Scaling**: Manual scaling (can be configured for auto-scaling)

### Running Deployment Locally (Optional)

```bash
cd mlops/deployment

# Set environment variables
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="guardian-ai-prod"
export AZURE_ML_WORKSPACE="guardian-ai-ml-workspace-prod"

# Deploy all models
python deploy_model.py

# Deploy specific model
python deploy_model.py --model-name nsfw-detector --version latest
```

---

## 📊 Monitoring & Verification

### Azure ML Studio

**View Training Jobs:**
1. Go to Azure ML Studio → Jobs
2. Filter by experiment name (`nsfw-detection`, `violence-detection`)
3. View metrics, logs, and artifacts

**View Registered Models:**
1. Go to Azure ML Studio → Models
2. View `nsfw-detector` and `violence-detector` models
3. Check model versions and metadata

**View Endpoints:**
1. Go to Azure ML Studio → Endpoints
2. Check endpoint status (Healthy/Unhealthy)
3. View scoring URIs and usage metrics

### Get Endpoint Information

```bash
# Get NSFW endpoint scoring URI
az ml online-endpoint show \
  --name nsfw-detector-endpoint \
  --resource-group guardian-ai-prod \
  --workspace-name guardian-ai-ml-workspace-prod \
  --query scoring_uri -o tsv

# Get endpoint key
az ml online-endpoint get-credentials \
  --name nsfw-detector-endpoint \
  --resource-group guardian-ai-prod \
  --workspace-name guardian-ai-ml-workspace-prod \
  --query primaryKey -o tsv
```

---

## 🔧 Configuration

### Environment Variables

**For MLOps (Training & Deployment):**
```bash
# Azure ML Configuration
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_RESOURCE_GROUP="guardian-ai-prod"
AZURE_ML_WORKSPACE="guardian-ai-ml-workspace-prod"
AZURE_ML_REGION="eastus"
COMPUTE_CLUSTER="cpu-training-cluster"
MLFLOW_TRACKING_URI="azureml://eastus.api.azureml.ms/mlflow/v1.0/..."
```

**For Application Services:**
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_REGION="us-east-1"
S3_BUCKET_NAME="guardian-videos-xxxxxxxx"
SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/.../guardian-video-processing"
SQS_GPU_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/.../guardian-gpu-processing"
DYNAMODB_VIDEOS_TABLE="guardian-videos"
DYNAMODB_EVENTS_TABLE="guardian-events"

# Azure ML Endpoints (after deployment)
NSFW_MODEL_ENDPOINT="https://nsfw-detector-endpoint.eastus.inference.ml.azure.com/score"
VIOLENCE_MODEL_ENDPOINT="https://violence-detector-endpoint.eastus.inference.ml.azure.com/score"
MODEL_ENDPOINT_KEY="your-endpoint-key"

# Optional: Azure OpenAI (disabled by default)
AZURE_OPENAI_ENABLED="false"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-api-key"
```

### Azure DevOps Variables

Configure in Variable Group `guardian-variables`:

- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_ML_WORKSPACE`
- `AZURE_ML_REGION`
- `COMPUTE_CLUSTER`

### Kubernetes ConfigMap

For Kubernetes deployments, Azure ML endpoint URLs are stored in ConfigMap:

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: guardian-config
data:
  NSFW_MODEL_ENDPOINT: "https://nsfw-detector-endpoint.eastus.inference.ml.azure.com/score"
  VIOLENCE_MODEL_ENDPOINT: "https://violence-detector-endpoint.eastus.inference.ml.azure.com/score"
  MODEL_ENDPOINT_KEY: "your-endpoint-key"
```

---

## 📚 Documentation

### Core Guides

- **[COMPUTE_CLUSTER_WORKFLOW.md](./docs/COMPUTE_CLUSTER_WORKFLOW.md)** - Complete workflow from Git to deployment
- **[AZURE_DEVOPS_ML_INTEGRATION_GUIDE.md](./docs/AZURE_DEVOPS_ML_INTEGRATION_GUIDE.md)** - Azure DevOps setup and configuration

### Key Concepts

- **Compute Cluster Training**: Models train on Azure ML compute clusters, not on pipeline agents
- **Automatic Model Registration**: Models are automatically registered after successful training
- **MLflow Integration**: All training metrics tracked in MLflow with Azure ML backend
- **Online Endpoints**: Models deployed as managed online endpoints for real-time inference

---

## 🐛 Troubleshooting

### Training Pipeline Issues

**Issue**: Compute cluster not found
```bash
# Verify cluster exists
az ml compute show \
  --name cpu-training-cluster \
  --workspace-name guardian-ai-ml-workspace-prod \
  --resource-group guardian-ai-prod
```

**Issue**: Model registration fails
- Check training logs in Azure ML Studio → Jobs → Outputs + logs
- Verify MLflow tracking URI is correctly configured
- Ensure model artifacts are saved successfully

### Deployment Pipeline Issues

**Issue**: Endpoint creation fails
```bash
# Check endpoint status
az ml online-endpoint show \
  --name nsfw-detector-endpoint \
  --resource-group guardian-ai-prod \
  --workspace-name guardian-ai-ml-workspace-prod
```

**Issue**: Model not found in registry
- Verify model is registered: Azure ML Studio → Models
- Check model name matches exactly (case-sensitive)
- Ensure training pipeline completed successfully

---

## ✅ Project Status

**Current Implementation:**
- ✅ Azure ML compute cluster training
- ✅ Automated model registration
- ✅ Azure DevOps CI/CD pipelines
- ✅ Online endpoint deployment
- ✅ MLflow tracking integration
- ✅ Kubernetes integration (ConfigMap updates)

**Production Ready:**
- ✅ Complete MLOps lifecycle
- ✅ Automated workflows
- ✅ Model versioning and registry
- ✅ Scalable compute infrastructure

---

## 🎓 Learning Outcomes

This project demonstrates:

- **MLOps Best Practices**: Complete lifecycle automation
- **Azure ML Integration**: Compute clusters, model registry, endpoints
- **CI/CD for ML**: Automated training and deployment pipelines
- **MLflow Tracking**: Experiment tracking and model management
- **Production Deployment**: Online endpoints with health monitoring

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: February 2026
