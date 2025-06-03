# SolarRally AWS Deployment Plan

## Overview
Deploying SolarRally to AWS will provide scalability, reliability, and enhanced IoT capabilities for managing multiple EV charging stations across different locations.

## Current Architecture Summary
- **Backend**: FastAPI with authentication, WebSocket support
- **Database**: PostgreSQL with user management and session tracking
- **MQTT**: Real-time telemetry from EVSE units
- **Frontend**: React/Next.js dashboard
- **Mock Publishers**: Simulated EVSE devices

## Recommended AWS Architecture

### Option 1: IoT-Optimized Architecture (Recommended)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EVSE Devices  │───▶│   AWS IoT Core   │───▶│  Lambda/ECS API │
│  (Real/Mock)    │    │    (MQTT)        │    │   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │◀───│   CloudFront     │    │  RDS PostgreSQL │
│   (S3 Bucket)   │    │   + S3 Static    │    │   (Managed DB)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### AWS Services Breakdown

#### 1. **AWS IoT Core** (MQTT Broker Replacement)
- **Purpose**: Managed MQTT broker with device management
- **Benefits**: 
  - Auto-scaling MQTT connections
  - Built-in device authentication & authorization
  - Integration with other AWS services
  - Device shadows for offline state management
  - Rules engine for real-time data processing

#### 2. **Compute Layer**
**Option A: ECS Fargate (Recommended)**
- Containerized FastAPI backend
- Auto-scaling based on load
- No server management

**Option B: AWS Lambda**
- Serverless functions for API endpoints
- Cost-effective for variable load
- May require refactoring for cold starts

#### 3. **Database: Amazon RDS PostgreSQL**
- Managed PostgreSQL instance
- Automated backups and patching
- Multi-AZ deployment for high availability
- Performance Insights for monitoring

#### 4. **Frontend: S3 + CloudFront**
- Static React build hosted on S3
- CloudFront CDN for global distribution
- Custom domain with SSL certificate

#### 5. **Additional Services**

| Service | Purpose | Benefit |
|---------|---------|---------|
| **Application Load Balancer** | API traffic distribution | High availability, SSL termination |
| **VPC** | Network isolation | Security, private subnets |
| **IAM** | Access control | Secure service-to-service communication |
| **CloudWatch** | Monitoring & logging | Performance metrics, alerting |
| **AWS WAF** | Web application firewall | DDoS protection, security |
| **Route 53** | DNS management | Custom domain, health checks |
| **Secrets Manager** | Store DB credentials | Secure credential rotation |

## Migration Strategy

### Phase 1: Infrastructure Setup (Week 1)
1. **VPC and Networking**
   ```bash
   # Create VPC with public/private subnets
   # Setup Internet Gateway and NAT Gateway
   # Configure Security Groups
   ```

2. **Database Migration**
   - Create RDS PostgreSQL instance
   - Migrate existing database schema
   - Update connection strings

3. **IoT Core Setup**
   - Configure IoT Core MQTT broker
   - Create IoT policies and certificates
   - Setup device authentication

### Phase 2: Application Deployment (Week 2)
1. **Backend Deployment**
   - Containerize FastAPI application
   - Deploy to ECS Fargate
   - Configure environment variables
   - Setup Application Load Balancer

2. **Frontend Deployment**
   - Build React application for production
   - Deploy to S3 bucket
   - Configure CloudFront distribution
   - Update API endpoints

### Phase 3: Testing & Optimization (Week 3)
1. **Integration Testing**
   - Test MQTT connectivity with IoT Core
   - Verify authentication flows
   - Test WebSocket connections through ALB

2. **Performance Optimization**
   - Configure auto-scaling policies
   - Setup CloudWatch monitoring
   - Optimize database queries

## Cost Estimation (Monthly)

### Small Deployment (1-10 EVSE units)
- **IoT Core**: ~$5-15 (based on message volume)
- **ECS Fargate**: ~$30-50 (2 vCPU, 4GB RAM)
- **RDS PostgreSQL**: ~$25-40 (db.t3.micro)
- **S3 + CloudFront**: ~$1-5
- **ALB**: ~$20
- **Total**: **~$80-130/month**

### Medium Deployment (10-100 EVSE units)
- **IoT Core**: ~$50-150
- **ECS Fargate**: ~$100-200 (with auto-scaling)
- **RDS PostgreSQL**: ~$100-200 (db.t3.small/medium)
- **S3 + CloudFront**: ~$5-15
- **ALB**: ~$20
- **Total**: **~$275-585/month**

## Implementation Files

### 1. Terraform Infrastructure (Infrastructure as Code)
```hcl
# terraform/main.tf
# VPC, subnets, security groups, RDS, IoT Core, ECS cluster
```

### 2. Docker Configuration
```dockerfile
# Dockerfile.production
# Optimized container for FastAPI backend
```

### 3. ECS Task Definition
```json
# ecs-task-definition.json
# Container configuration, environment variables, resources
```

### 4. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
# Automated deployment to AWS using GitHub Actions
```

## Security Considerations

1. **Network Security**
   - Private subnets for backend and database
   - Security groups with minimal required access
   - VPC endpoints for AWS services

2. **IoT Security**
   - X.509 certificates for device authentication
   - IoT policies for fine-grained permissions
   - Device-specific credentials

3. **Application Security**
   - WAF rules for common attacks
   - Secrets Manager for sensitive data
   - IAM roles with least privilege

4. **Data Protection**
   - RDS encryption at rest
   - SSL/TLS for all connections
   - CloudTrail for audit logging

## Benefits of AWS Deployment

### Scalability
- **Auto-scaling**: Handle varying loads automatically
- **Global reach**: Deploy to multiple regions as you expand
- **Device management**: AWS IoT Device Management for fleet operations

### Reliability
- **High availability**: Multi-AZ deployments
- **Backup & recovery**: Automated RDS backups
- **Disaster recovery**: Cross-region replication options

### Operations
- **Monitoring**: CloudWatch dashboards and alerts
- **Logging**: Centralized log management
- **Updates**: Rolling deployments with zero downtime

### Cost Efficiency
- **Pay-as-you-go**: Only pay for resources used
- **Reserved instances**: Significant savings for predictable workloads
- **Spot instances**: Cost savings for non-critical workloads

## Next Steps

1. **AWS Account Setup**
   - Create AWS account if needed
   - Setup billing alerts
   - Configure IAM users and roles

2. **Domain Registration**
   - Register domain for the application
   - Configure Route 53 hosted zone

3. **SSL Certificate**
   - Request ACM certificate for custom domain
   - Configure for CloudFront and ALB

4. **Infrastructure Deployment**
   - Deploy using Terraform or CloudFormation
   - Configure monitoring and alerting

Would you like me to start with any specific component or create the Terraform configuration files? 