# Guardian AI - Simplified MLOps Video Moderation System

**Risk-Based, Near-Real-Time Video Moderation with Simplified Multi-Cloud MLOps**

## 🎯 Project Overview

Enterprise-grade AI-assisted video moderation system with:
- **Risk-adaptive processing** (0.5-1 FPS, not 30 FPS)
- **CPU-first, GPU-on-demand** architecture
- **Human-in-the-loop** review system
- **Simplified multi-cloud** (AWS storage/queue/DB, Azure compute/ML)
- **Complete MLOps lifecycle** (training, deployment, monitoring)
- **50% cost reduction** vs original architecture

---

## 📊 Simplified Architecture Highlights

### What's Included (Minimal Learning Setup)
✅ **AWS Services (3)**:
- S3 - Video storage
- SQS - 2 queues (video-processing, gpu-processing)
- DynamoDB - 2 tables (videos, events)

✅ **Azure Services (2-3)**:
- AKS - Kubernetes cluster
- ACR - Container registry
- Azure ML - Model Registry (optional)

✅ **Microservices (6)**:
- Ingestion, Fast Screening, Deep Vision, Policy Engine, Human Review, Notification

✅ **Open Source (3)**:
- Redis (caching), KEDA (GPU autoscaling), Prometheus + Grafana (monitoring)

**Total: 9 core services** (down from 15+)

### What's Removed (Simplified for Learning)
❌ Azure Front Door + CDN → Use NGINX Ingress
❌ WAF + DDoS Protection → Use Kubernetes NetworkPolicies
❌ API Management → Direct service communication
❌ 2 extra SQS queues → Use direct HTTP calls
❌ 2 extra DynamoDB tables → Consolidated into videos table

### Optional Features (Disabled by Default)
⚠️ **Azure OpenAI** - Set `AZURE_OPENAI_ENABLED=true` to enable LLM features
⚠️ **S3 Glacier Lifecycle** - Uncomment in setup-aws.sh for archiving
⚠️ **Azure ML Advanced** - A/B testing, drift detection (document separately)

---

## 💰 Cost Comparison

### Original Architecture
- AWS: ~$50-100/month (4 SQS + 4 DynamoDB + S3)
- Azure: ~$200-400/month (AKS + ACR + Azure ML + OpenAI + Monitoring)
- **Total: $250-500/month**

### Simplified Architecture
- AWS: ~$25-40/month (2 SQS + 2 DynamoDB + S3)
- Azure: ~$100-150/month (AKS + ACR, minimal Azure ML)
- **Total: $125-190/month**

**Savings: ~50-60% reduction**

### Cost Breakdown (Monthly)
| Component | Original | Simplified | Savings |
|-----------|----------|------------|---------|
| AWS SQS | $2-4 (4 queues) | $1-2 (2 queues) | 50% |
| AWS DynamoDB | $20-40 (4 tables) | $10-20 (2 tables) | 50% |
| AWS S3 | $5-10 | $5-10 | 0% |
| Azure AKS | $150-250 | $100-150 | 33% |
| Azure Monitoring | $20-50 | $0 (use Prometheus) | 100% |
| Azure OpenAI | $20-100 | $0 (optional) | 100% |
| **Total** | **$250-500** | **$125-190** | **~50%** |

---

## 📋 Prerequisites

### Required Accounts
- AWS account (primary: S3, SQS, DynamoDB)
- Azure subscription (for AKS deployment)
- GitHub account (for CI/CD)

### Local Development Tools
```bash
# Required
- Docker Desktop 24+
- kubectl 1.28+
- Python 3.11+
- AWS CLI 2.13+
- Azure CLI 2.50+

# Optional
- k9s (Kubernetes UI)
- Lens (Kubernetes IDE)
```

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Learning)
```bash
# 1. Clone repository
git clone https://github.com/yourusername/guardian-ai.git
cd guardian-ai

# 2. Setup AWS resources (2 queues, 2 tables)
bash scripts/setup-aws.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# 4. Start all services
docker-compose up --build

# 5. Test
curl http://localhost:8000/health
```

**Time**: ~30 minutes
**Cost**: ~$10-25/month (AWS only)

### Option 2: Cloud Deployment (Production)
```bash
# 1. Setup AWS resources
bash scripts/setup-aws.sh

# 2. Setup Azure AKS
bash scripts/setup-aks.sh

# 3. Build and push images
bash scripts/build-services.sh

# 4. Deploy to Kubernetes
kubectl apply -f k8s/

# 5. Verify deployment
kubectl get pods -n production
```

**Time**: ~2-3 hours
**Cost**: ~$125-190/month

---

## 📖 Documentation

### Getting Started
- **[LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md)** - Complete local setup guide (⭐ Start here!)
- **[ARCHITECTURE_CORRECTED.md](./ARCHITECTURE_CORRECTED.md)** - Simplified architecture details
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture diagrams

### Deployment & Operations
- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - Deployment instructions
- **[PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)** - Project organization

### Optional Features
- **[AZURE_OPENAI_INTEGRATION.md](./AZURE_OPENAI_INTEGRATION.md)** - Enable LLM features
- **[AWS_MIGRATION_SUMMARY.md](./AWS_MIGRATION_SUMMARY.md)** - Multi-cloud strategy

---

## 🏗️ Build Guide: 0 to Production

### **Phase 1: Foundation Setup (30 minutes)**

#### Step 1.1: Initialize Project
```bash
cd ~/Projects/MLOps_Project
bash scripts/init-project.sh
```

#### Step 1.2: Setup AWS Resources (Simplified)
```bash
bash scripts/setup-aws.sh
# Creates: 1 S3 bucket, 2 SQS queues, 2 DynamoDB tables
```

#### Step 1.3: Configure Environment
```bash
# Create .env file with AWS credentials
cat > .env <<EOF
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=guardian-videos-xxxxxxxx
SQS_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/...
SQS_GPU_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/...
DYNAMODB_VIDEOS_TABLE=guardian-videos
DYNAMODB_EVENTS_TABLE=guardian-events
EOF
```

---

### **Phase 2: Local Development (30 minutes)**

#### Step 2.1: Start Services
```bash
docker-compose up --build
```

#### Step 2.2: Test Upload
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@test-video.mp4"
```

#### Step 2.3: Verify Data
```bash
# Check DynamoDB
aws dynamodb scan --table-name guardian-videos --limit 5

# Check S3
aws s3 ls s3://guardian-videos-xxxxxxxx/videos/

# Check SQS
aws sqs get-queue-attributes --queue-url $SQS_QUEUE_URL
```

---

### **Phase 3: Cloud Deployment (Optional, 2-3 hours)**

#### Step 3.1: Create AKS Cluster
```bash
bash scripts/setup-aks.sh
```

#### Step 3.2: Build and Push Images
```bash
bash scripts/build-services.sh
```

#### Step 3.3: Deploy Services
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/cpu-services/
kubectl apply -f k8s/gpu-services/
```

#### Step 3.4: Verify Deployment
```bash
kubectl get pods -n production
kubectl get svc -n production
```

---

## 🎯 SLOs & Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| P95 Processing Time (Low-Risk) | < 15s | Application logs |
| P95 Processing Time (High-Risk) | < 60s | Application logs |
| GPU Utilization | > 70% when active | Cluster metrics |
| API Availability | 99.9% | Service health checks |
| False Positive Rate | < 5% | Human review feedback |
| Cost per 1000 videos | < $2.00 | AWS Cost Management |

---

## 🔧 Key Features

### 1. Risk-Adaptive Processing
- **0.5 FPS** for CPU screening (fast, cost-effective)
- **1 FPS** for GPU analysis (balance accuracy and cost)
- **80% of videos** skip GPU analysis (cost savings)

### 2. GPU Scale-to-Zero
- KEDA monitors queue depth
- Scales from 0 → 5 replicas based on demand
- **90% cost savings** during off-peak hours

### 3. Simplified Multi-Cloud
- **AWS**: Storage, queues, database (S3, SQS, DynamoDB)
- **Azure**: Compute, ML (AKS, ACR, Azure ML)
- **Design**: Best-of-both-clouds, minimal services

### 4. Human-in-the-Loop
- Confidence score between 0.2 - 0.8 triggers review
- 4-hour SLA for review completion
- Optional AI copilot for reviewers

### 5. Optional Azure OpenAI Integration
- **Default**: Disabled (`AZURE_OPENAI_ENABLED=false`)
- **Use Cases**: Human review copilot, policy interpretation
- **Cost**: ~$0.01-0.02 per request
- **Enable**: Set `AZURE_OPENAI_ENABLED=true` in .env

---

## 📊 Data Flow

```
1. Upload Video → Ingestion Service
   ↓
2. Store in S3 + Create DynamoDB record
   ↓
3. Send to SQS (video-processing queue)
   ↓
4. Fast Screening (CPU) - 0.5 FPS
   ↓
5. If risk > 0.3 → Send to GPU queue
   ↓
6. Deep Vision (GPU) - 1 FPS (optional)
   ↓
7. Policy Engine - Make decision
   ↓
8. If score 0.2-0.8 → Human Review
   ↓
9. Notification Service - Send webhook
```

---

## 🧪 Testing

### Unit Tests
```bash
cd services/ingestion
pytest tests/
```

### Integration Tests
```bash
bash scripts/integration-test.sh
```

### Load Testing
```bash
bash scripts/load-test.sh
```

---

## 🔒 Security Best Practices

1. **AWS Credentials**: Use IAM roles in production, never commit credentials
2. **Secrets Management**: Use Kubernetes secrets for sensitive data
3. **Network Policies**: Implement Kubernetes NetworkPolicies
4. **HTTPS**: Use TLS/SSL for all external communication
5. **API Authentication**: Implement API keys or OAuth2

---

## 🆘 Troubleshooting

### Issue: Services can't connect to AWS
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check environment variables
docker-compose config | grep AWS
```

### Issue: DynamoDB table not found
```bash
# List tables
aws dynamodb list-tables --region ap-south-1

# Verify table exists
aws dynamodb describe-table --table-name guardian-videos
```

### Issue: Docker Compose fails
```bash
# View logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up
```

See [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md) for more troubleshooting tips.

---

## 📚 Learning Path

### Beginner (Local Development)
1. ✅ Setup AWS resources (S3, SQS, DynamoDB)
2. ✅ Run services locally with docker-compose
3. ✅ Test video upload and processing
4. ✅ Understand data flow and architecture

**Time**: 2-3 hours
**Cost**: ~$10-25/month

### Intermediate (Cloud Deployment)
1. ⏳ Deploy to Azure AKS
2. ⏳ Setup NGINX Ingress
3. ⏳ Configure monitoring with Prometheus + Grafana
4. ⏳ Implement CI/CD with GitHub Actions

**Time**: 1-2 days
**Cost**: ~$125-190/month

### Advanced (MLOps & Optimization)
1. ⏳ Setup Azure ML for model training
2. ⏳ Implement A/B testing
3. ⏳ Add drift detection
4. ⏳ Multi-region deployment
5. ⏳ Advanced security (WAF, DDoS protection)

**Time**: 1-2 weeks
**Cost**: ~$250-500/month

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

---

## 🙏 Acknowledgments

- Built for learning purposes
- Designed for cost-effectiveness
- Optimized for simplicity

---

## 📞 Support

- **Documentation**: See [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md)
- **Issues**: Open a GitHub issue
- **Questions**: Check documentation first

---

## 🎓 Educational Value

This project teaches:
- ✅ Multi-cloud architecture (AWS + Azure)
- ✅ Microservices design patterns
- ✅ Kubernetes deployment and scaling
- ✅ MLOps lifecycle (training, deployment, monitoring)
- ✅ Cost optimization strategies
- ✅ Human-in-the-loop AI systems
- ✅ Asynchronous processing with queues
- ✅ Database design (NoSQL with DynamoDB)
- ✅ Docker containerization
- ✅ CI/CD with GitHub Actions

---

**Status**: ✅ Simplified & Production Ready
**Version**: 2.0 (Simplified)
**Cost**: ~$125-190/month (50% reduction)
**Services**: 9 core services (down from 15+)

🚀 **Start learning MLOps today!**
# MultiCloud_MLOps
