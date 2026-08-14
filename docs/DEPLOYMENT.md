# Cloud Deployment Guide

This guide covers deploying the AI Trip Agent to various cloud platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Deployment](#aws-deployment)
3. [GCP Deployment](#gcp-deployment)
4. [Azure Deployment](#azure-deployment)
5. [General Cloud Considerations](#general-cloud-considerations)
6. [Security Best Practices](#security-best-practices)
7. [Monitoring and Logging](#monitoring-and-logging)

---

## Prerequisites

Before deploying to any cloud platform:

- [ ] Test the application locally
- [ ] Prepare production `.env` file
- [ ] Set up domain name (optional)
- [ ] Obtain SSL/TLS certificates
- [ ] Configure API keys for production LLM provider
- [ ] Backup vector store data
- [ ] Set up monitoring and alerting

---

## AWS Deployment

### Option 1: EC2 Instance (Simplest)

#### 1. Launch EC2 Instance

```bash
# Instance specifications:
# - Type: t3.medium or larger (2 vCPU, 4GB RAM minimum)
# - OS: Ubuntu 22.04 LTS
# - Storage: 30GB+ SSD
# - Security Group: Allow ports 22, 80, 443, 8001, 8516, 8002
```

#### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <your-repo-url>
cd ai-trip-agent

# Configure environment
cp .env.example .env
nano .env  # Edit with production settings
```

#### 3. Deploy Application

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Configure Nginx (Optional)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/ai-trip-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Streamlit UI
    location / {
        proxy_pass http://localhost:8516;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # FastAPI Backend
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-trip-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### Option 2: ECS (Elastic Container Service)

#### 1. Create ECR Repositories

```bash
# Create repositories for API and UI
aws ecr create-repository --repository-name ai-trip-agent-api
aws ecr create-repository --repository-name ai-trip-agent-ui
```

#### 2. Build and Push Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push API
docker build -f Dockerfile.api -t ai-trip-agent-api .
docker tag ai-trip-agent-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-agent-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-agent-api:latest

# Build and push UI
docker build -f Dockerfile.ui -t ai-trip-agent-ui .
docker tag ai-trip-agent-ui:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-agent-ui:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-agent-ui:latest
```

#### 3. Create ECS Task Definitions

Create task definitions for:
- ChromaDB service
- FastAPI backend
- Streamlit UI

#### 4. Deploy to ECS

Use AWS Console or CLI to:
- Create ECS cluster
- Create services from task definitions
- Configure load balancer
- Set up auto-scaling

### Option 3: EKS (Kubernetes)

See Kubernetes deployment section below.

---

## GCP Deployment

### Option 1: Compute Engine VM

Similar to AWS EC2 deployment:

```bash
# Create VM instance
gcloud compute instances create ai-trip-agent \
    --machine-type=e2-medium \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --tags=http-server,https-server

# SSH into instance
gcloud compute ssh ai-trip-agent

# Follow same setup steps as AWS EC2
```

### Option 2: Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-trip-agent-api -f Dockerfile.api
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-trip-agent-ui -f Dockerfile.ui

# Deploy to Cloud Run
gcloud run deploy ai-trip-agent-api \
    --image gcr.io/PROJECT_ID/ai-trip-agent-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

gcloud run deploy ai-trip-agent-ui \
    --image gcr.io/PROJECT_ID/ai-trip-agent-ui \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

---

## Azure Deployment

### Option 1: Azure VM

```bash
# Create resource group
az group create --name ai-trip-agent-rg --location eastus

# Create VM
az vm create \
    --resource-group ai-trip-agent-rg \
    --name ai-trip-agent-vm \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username azureuser \
    --generate-ssh-keys

# Open ports
az vm open-port --port 80 --resource-group ai-trip-agent-rg --name ai-trip-agent-vm
az vm open-port --port 443 --resource-group ai-trip-agent-rg --name ai-trip-agent-vm

# SSH and setup
ssh azureuser@<vm-ip>
# Follow same setup steps as AWS EC2
```

### Option 2: Azure Container Instances

```bash
# Create container registry
az acr create --resource-group ai-trip-agent-rg --name aitripagentacr --sku Basic

# Build and push images
az acr build --registry aitripagentacr --image ai-trip-agent-api:latest -f Dockerfile.api .
az acr build --registry aitripagentacr --image ai-trip-agent-ui:latest -f Dockerfile.ui .

# Deploy container instances
az container create \
    --resource-group ai-trip-agent-rg \
    --name ai-trip-agent-api \
    --image aitripagentacr.azurecr.io/ai-trip-agent-api:latest \
    --dns-name-label ai-trip-agent-api \
    --ports 8001
```

---

## General Cloud Considerations

### Environment Variables

Store sensitive data in cloud secret managers:

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
    --name ai-trip-agent/env \
    --secret-string file://.env
```

**GCP Secret Manager:**
```bash
gcloud secrets create ai-trip-agent-env --data-file=.env
```

**Azure Key Vault:**
```bash
az keyvault create --name ai-trip-agent-kv --resource-group ai-trip-agent-rg
az keyvault secret set --vault-name ai-trip-agent-kv --name env --file .env
```

### Persistent Storage

**ChromaDB Data:**
- AWS: Use EBS volumes or EFS
- GCP: Use Persistent Disks or Filestore
- Azure: Use Managed Disks or Azure Files

### Load Balancing

- AWS: Application Load Balancer (ALB)
- GCP: Cloud Load Balancing
- Azure: Azure Load Balancer

### Auto-Scaling

Configure auto-scaling based on:
- CPU utilization (> 70%)
- Memory usage (> 80%)
- Request count
- Response time

---

## Security Best Practices

### 1. Network Security

```bash
# Firewall rules (example for AWS Security Group)
- Allow inbound: 80 (HTTP), 443 (HTTPS) from 0.0.0.0/0
- Allow inbound: 22 (SSH) from your IP only
- Block direct access to: 8001, 8002, 8516
- Use VPC for internal communication
```

### 2. API Authentication

Add API key authentication:

```python
# In .env
API_KEY=your-secure-random-key

# In FastAPI
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### 3. HTTPS Only

- Use SSL/TLS certificates
- Redirect HTTP to HTTPS
- Enable HSTS headers

### 4. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/plan-trip")
@limiter.limit("10/minute")
async def plan_trip(request: Request, ...):
    ...
```

### 5. Input Validation

- Validate all user inputs
- Sanitize queries
- Limit request sizes
- Use Pydantic models

---

## Monitoring and Logging

### 1. Application Logging

```python
# Use structured logging
import logging
import json

logger = logging.getLogger(__name__)

# Log to JSON for cloud log aggregation
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
))
logger.addHandler(handler)
```

### 2. Cloud Monitoring

**AWS CloudWatch:**
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

**GCP Cloud Monitoring:**
```bash
# Logs are automatically collected from Cloud Run
# View in Cloud Console > Logging
```

**Azure Monitor:**
```bash
# Enable Application Insights
az monitor app-insights component create \
    --app ai-trip-agent \
    --location eastus \
    --resource-group ai-trip-agent-rg
```

### 3. Health Checks

Configure health check endpoints:
- `/health` - Basic health check
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

### 4. Alerts

Set up alerts for:
- High error rates (> 5%)
- Slow response times (> 5s)
- High CPU/memory usage (> 80%)
- Service downtime
- ChromaDB connection failures

---

## Backup and Disaster Recovery

### 1. Vector Store Backup

```bash
# Backup ChromaDB data
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz chroma_data/

# Upload to cloud storage
# AWS S3
aws s3 cp chroma-backup-*.tar.gz s3://your-backup-bucket/

# GCP Cloud Storage
gsutil cp chroma-backup-*.tar.gz gs://your-backup-bucket/

# Azure Blob Storage
az storage blob upload --file chroma-backup-*.tar.gz --container backups
```

### 2. Automated Backups

Create a cron job:

```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### 3. Disaster Recovery Plan

1. Keep backups in multiple regions
2. Document recovery procedures
3. Test recovery process regularly
4. Maintain infrastructure as code (Terraform/CloudFormation)

---

## Cost Optimization

### 1. Right-Sizing

- Start with smaller instances
- Monitor resource usage
- Scale up only when needed

### 2. Reserved Instances

- Use reserved instances for predictable workloads
- Save 30-70% compared to on-demand

### 3. Spot Instances

- Use spot instances for non-critical workloads
- Save up to 90% on compute costs

### 4. Auto-Scaling

- Scale down during low-traffic periods
- Set minimum and maximum instance counts

---

## Troubleshooting

### Common Issues

**1. ChromaDB Connection Timeout**
- Check security group/firewall rules
- Verify ChromaDB container is running
- Check network connectivity

**2. High Memory Usage**
- Reduce `RAG_TOP_K`
- Use smaller embedding models
- Implement caching

**3. Slow Response Times**
- Enable LLM response streaming
- Optimize vector search
- Add caching layer (Redis)

**4. SSL Certificate Issues**
- Verify domain DNS settings
- Check certificate expiration
- Renew certificates before expiry

---

## Maintenance

### Regular Tasks

- [ ] Update dependencies monthly
- [ ] Review and rotate API keys quarterly
- [ ] Check and optimize database performance
- [ ] Review logs for errors and warnings
- [ ] Test backup and recovery procedures
- [ ] Update SSL certificates before expiry
- [ ] Monitor and optimize costs

---

## Support

For deployment issues:
1. Check application logs
2. Review cloud provider documentation
3. Test locally first
4. Use cloud provider support channels

---

**Remember:** Always test in a staging environment before deploying to production!
