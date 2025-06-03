# SolarRally AWS Deployment - Getting Started Guide

## Prerequisites

Before deploying SolarRally to AWS, ensure you have the following installed and configured:

### Required Tools
1. **AWS CLI** - [Install AWS CLI](https://aws.amazon.com/cli/)
2. **Terraform** - [Install Terraform](https://developer.hashicorp.com/terraform/downloads)
3. **Docker Desktop** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
4. **Git** - For cloning and version control

### AWS Account Setup
1. **AWS Account** - Create an AWS account if you don't have one
2. **IAM User** - Create an IAM user with programmatic access
3. **Required Permissions** - Attach the following managed policies to your IAM user:
   - `AmazonEC2FullAccess`
   - `AmazonECSFullAccess`
   - `AmazonRDSFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonVPCFullAccess`
   - `IAMFullAccess`
   - `AWSIoTFullAccess`
   - `AmazonRoute53FullAccess`
   - `AWSCertificateManagerFullAccess`

### AWS CLI Configuration
```bash
# Configure AWS CLI with your credentials
aws configure
# Enter your Access Key ID, Secret Access Key, region, and output format
```

## Quick Start Deployment

### Step 1: Prepare the Project
```bash
# Navigate to the project directory
cd /path/to/SolarRally

# Make sure you're on the correct branch
git checkout main
git pull origin main
```

### Step 2: Configure Variables (Optional)
Edit the variables in `terraform/main.tf` if you want to customize:
- Project name
- Environment (dev/staging/prod)
- AWS region
- Domain name

### Step 3: Deploy Infrastructure

#### Option A: Automated Deployment (Linux/macOS)
```bash
# Make script executable (Linux/macOS only)
chmod +x scripts/deploy_to_aws.sh

# Run full deployment
./scripts/deploy_to_aws.sh deploy dev us-east-1 default

# Or deploy only infrastructure first
./scripts/deploy_to_aws.sh infrastructure-only dev us-east-1 default
```

#### Option B: Manual Deployment (Windows/All Platforms)

**Deploy Infrastructure:**
```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="project_name=solarrally" -var="environment=dev" -var="region=us-east-1" -out=tfplan

# Apply deployment
terraform apply tfplan

# Get important outputs
terraform output
```

**Build and Push Docker Image:**
```bash
# Get ECR repository URL from Terraform output
cd terraform
$ECR_URL = terraform output -raw ecr_repository_url
cd ..

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Build and tag image
cd backend
docker build -f Dockerfile.production -t solarrally-backend:latest .
docker tag solarrally-backend:latest ${ECR_URL}:latest

# Push image
docker push ${ECR_URL}:latest
cd ..
```

**Update ECS Service:**
```bash
# Get cluster and service names
cd terraform
$CLUSTER_NAME = terraform output -raw ecs_cluster_name
$SERVICE_NAME = terraform output -raw ecs_service_name
cd ..

# Force new deployment
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --region us-east-1
```

### Step 4: Configure Domain (Optional)
If you have a custom domain:

1. **Get ALB DNS name:**
   ```bash
   cd terraform
   terraform output alb_dns_name
   ```

2. **Create Route 53 hosted zone** (if using Route 53)
3. **Create CNAME record** pointing your domain to the ALB DNS name
4. **Request SSL certificate** in AWS Certificate Manager
5. **Update ALB listener** to use HTTPS with the certificate

### Step 5: Update Application Configuration

**Update MQTT Configuration:**
```bash
# Get IoT Core endpoint
cd terraform
terraform output iot_endpoint
```

Update your EVSE devices and mock publishers to use the AWS IoT Core endpoint instead of localhost:1883.

**Update Frontend Configuration:**
Update your frontend to point to the new ALB endpoint instead of localhost:8000.

## Deployment Verification

### Check Application Health
```bash
# Get ALB DNS name
cd terraform
$ALB_DNS = terraform output -raw alb_dns_name
cd ..

# Test health endpoint
curl http://$ALB_DNS/health

# Test API endpoint
curl http://$ALB_DNS/api/v1/evse/units
```

### Monitor Logs
```bash
# View ECS logs in CloudWatch
aws logs describe-log-groups --log-group-name-prefix "/ecs/solarrally"

# Stream logs
aws logs tail /ecs/solarrally-dev --follow
```

### Check ECS Service Status
```bash
# Get service status
aws ecs describe-services --cluster solarrally-dev-cluster --services solarrally-dev-backend
```

## Cost Management

### Monitor Costs
- Set up AWS Billing Alerts
- Use AWS Cost Explorer to track spending
- Consider using AWS Budgets for cost control

### Cost Optimization
- Use Reserved Instances for predictable workloads
- Consider Spot Instances for non-critical tasks
- Right-size your RDS instance based on usage
- Set up auto-scaling to handle variable loads

## Security Considerations

### Network Security
- All backend services run in private subnets
- Database is not publicly accessible
- Security groups restrict access to necessary ports only

### Secrets Management
- Database credentials stored in AWS Secrets Manager
- No hardcoded credentials in application code
- IAM roles used for service-to-service authentication

### IoT Security
- X.509 certificates for device authentication
- Fine-grained IoT policies for device permissions
- Secure MQTT over TLS

## Troubleshooting

### Common Issues

**Terraform Deployment Fails:**
- Check AWS permissions
- Ensure region availability zones support required services
- Verify resource naming conflicts

**Docker Build Fails:**
- Check that all dependencies are in requirements.txt
- Ensure Docker Desktop is running
- Verify Dockerfile syntax

**ECS Service Won't Start:**
- Check CloudWatch logs for errors
- Verify environment variables and secrets
- Ensure security groups allow necessary traffic

**Database Connection Issues:**
- Verify RDS security group allows connections from ECS
- Check database endpoint and credentials
- Ensure database is in the same VPC as ECS

### Getting Help
- Check CloudWatch logs for detailed error messages
- Use AWS Support for infrastructure issues
- Review Terraform state for resource conflicts

## Cleanup

To avoid ongoing charges, destroy the infrastructure when not needed:

```bash
cd terraform
terraform destroy -var="project_name=solarrally" -var="environment=dev" -var="region=us-east-1"
```

**Warning:** This will permanently delete all resources and data!

## Next Steps

After successful deployment:

1. **Set up monitoring** with CloudWatch dashboards
2. **Configure backups** for RDS database
3. **Set up CI/CD pipeline** for automated deployments
4. **Implement log aggregation** for better observability
5. **Set up alerts** for critical system metrics
6. **Plan scaling strategy** for production workloads

## Production Considerations

Before going to production:

1. **Enable deletion protection** on critical resources
2. **Set up multi-AZ deployment** for high availability
3. **Configure SSL/TLS** with ACM certificates
4. **Implement proper backup strategy**
5. **Set up comprehensive monitoring and alerting**
6. **Conduct security review and penetration testing**
7. **Plan disaster recovery procedures**

## Support

For questions or issues:
- Check the AWS documentation
- Review CloudWatch logs and metrics
- Consider AWS Support plans for production workloads 