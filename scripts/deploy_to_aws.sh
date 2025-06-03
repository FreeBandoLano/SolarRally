#!/bin/bash
# SolarRally AWS Deployment Script
# Automates the deployment process to AWS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="solarrally"
ENVIRONMENT=${1:-dev}
AWS_REGION=${2:-us-east-1}
AWS_PROFILE=${3:-default}

echo -e "${BLUE}🚀 Starting SolarRally AWS Deployment${NC}"
echo -e "${BLUE}   Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}   Region: ${AWS_REGION}${NC}"
echo -e "${BLUE}   AWS Profile: ${AWS_PROFILE}${NC}"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists terraform; then
    echo -e "${RED}❌ Terraform is not installed${NC}"
    exit 1
fi

if ! command_exists aws; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Check AWS credentials
echo -e "${YELLOW}🔐 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity --profile $AWS_PROFILE >/dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured or invalid${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials valid${NC}"

# Set up Terraform backend (optional - for state management)
setup_terraform_backend() {
    echo -e "${YELLOW}🗃️  Setting up Terraform backend...${NC}"
    
    # Create S3 bucket for state if it doesn't exist
    BUCKET_NAME="${PROJECT_NAME}-${ENVIRONMENT}-terraform-state-$(date +%s)"
    
    if ! aws s3 ls "s3://${BUCKET_NAME}" --profile $AWS_PROFILE >/dev/null 2>&1; then
        aws s3 mb "s3://${BUCKET_NAME}" --region $AWS_REGION --profile $AWS_PROFILE
        echo -e "${GREEN}✅ Created Terraform state bucket: ${BUCKET_NAME}${NC}"
    fi
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket $BUCKET_NAME \
        --versioning-configuration Status=Enabled \
        --profile $AWS_PROFILE
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️  Deploying infrastructure with Terraform...${NC}"
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan \
        -var="project_name=${PROJECT_NAME}" \
        -var="environment=${ENVIRONMENT}" \
        -var="region=${AWS_REGION}" \
        -out=tfplan
    
    # Apply deployment
    echo -e "${YELLOW}🚀 Applying Terraform changes...${NC}"
    terraform apply tfplan
    
    # Get outputs
    ECR_URL=$(terraform output -raw ecr_repository_url)
    ALB_DNS=$(terraform output -raw alb_dns_name)
    RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
    IOT_ENDPOINT=$(terraform output -raw iot_endpoint)
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
    echo -e "${BLUE}   ECR Repository: ${ECR_URL}${NC}"
    echo -e "${BLUE}   Load Balancer: ${ALB_DNS}${NC}"
    echo -e "${BLUE}   Database: ${RDS_ENDPOINT}${NC}"
    echo -e "${BLUE}   IoT Endpoint: ${IOT_ENDPOINT}${NC}"
    
    cd ..
}

# Build and push Docker image
build_and_push_image() {
    echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
    
    # Get ECR URL from Terraform output
    cd terraform
    ECR_URL=$(terraform output -raw ecr_repository_url)
    cd ..
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
        docker login --username AWS --password-stdin $ECR_URL
    
    # Build image
    cd backend
    docker build -f Dockerfile.production -t ${PROJECT_NAME}-backend:latest .
    
    # Tag image for ECR
    docker tag ${PROJECT_NAME}-backend:latest $ECR_URL:latest
    docker tag ${PROJECT_NAME}-backend:latest $ECR_URL:$(date +%Y%m%d%H%M%S)
    
    # Push image
    docker push $ECR_URL:latest
    docker push $ECR_URL:$(date +%Y%m%d%H%M%S)
    
    echo -e "${GREEN}✅ Docker image pushed successfully${NC}"
    cd ..
}

# Update ECS service
update_ecs_service() {
    echo -e "${YELLOW}🔄 Updating ECS service...${NC}"
    
    cd terraform
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
    SERVICE_NAME=$(terraform output -raw ecs_service_name)
    cd ..
    
    # Force new deployment
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --force-new-deployment \
        --region $AWS_REGION \
        --profile $AWS_PROFILE
    
    echo -e "${GREEN}✅ ECS service updated${NC}"
}

# Wait for deployment to complete
wait_for_deployment() {
    echo -e "${YELLOW}⏳ Waiting for deployment to complete...${NC}"
    
    cd terraform
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
    SERVICE_NAME=$(terraform output -raw ecs_service_name)
    cd ..
    
    aws ecs wait services-stable \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --profile $AWS_PROFILE
    
    echo -e "${GREEN}✅ Deployment completed successfully${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}📊 Running database migrations...${NC}"
    
    # This would typically run Alembic migrations
    # For now, we'll just note that this should be done
    echo -e "${YELLOW}ℹ️  Database migrations should be run separately${NC}"
    echo -e "${YELLOW}   Consider using AWS ECS Exec or a separate migration task${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}🏥 Performing health check...${NC}"
    
    cd terraform
    ALB_DNS=$(terraform output -raw alb_dns_name)
    cd ..
    
    # Wait a bit for the service to start
    sleep 30
    
    # Try to hit the health endpoint
    if curl -f "http://${ALB_DNS}/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is healthy${NC}"
        echo -e "${GREEN}🌐 Application URL: http://${ALB_DNS}${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check failed - application may still be starting${NC}"
        echo -e "${YELLOW}   Check logs in CloudWatch or try again in a few minutes${NC}"
    fi
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
    cd terraform
    rm -f tfplan
    cd ..
}

# Main deployment flow
main() {
    # setup_terraform_backend  # Uncomment if you want remote state
    deploy_infrastructure
    build_and_push_image
    update_ecs_service
    wait_for_deployment
    run_migrations
    health_check
    cleanup
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "=========================================="
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "${BLUE}1. Configure your domain/DNS to point to the ALB${NC}"
    echo -e "${BLUE}2. Set up SSL certificate using AWS Certificate Manager${NC}"
    echo -e "${BLUE}3. Update your frontend to use the new API endpoint${NC}"
    echo -e "${BLUE}4. Configure your EVSE devices to use AWS IoT Core${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "infrastructure-only")
        deploy_infrastructure
        ;;
    "image-only")
        build_and_push_image
        update_ecs_service
        wait_for_deployment
        ;;
    "destroy")
        echo -e "${RED}⚠️  Destroying infrastructure...${NC}"
        cd terraform
        terraform destroy \
            -var="project_name=${PROJECT_NAME}" \
            -var="environment=${ENVIRONMENT}" \
            -var="region=${AWS_REGION}"
        cd ..
        echo -e "${GREEN}✅ Infrastructure destroyed${NC}"
        ;;
    "help")
        echo "Usage: $0 [deploy|infrastructure-only|image-only|destroy|help] [environment] [region] [aws-profile]"
        echo ""
        echo "Commands:"
        echo "  deploy             - Full deployment (default)"
        echo "  infrastructure-only - Deploy only Terraform infrastructure"
        echo "  image-only         - Build and deploy only the Docker image"
        echo "  destroy            - Destroy all infrastructure"
        echo "  help               - Show this help"
        echo ""
        echo "Parameters:"
        echo "  environment        - Deployment environment (default: dev)"
        echo "  region             - AWS region (default: us-east-1)"
        echo "  aws-profile        - AWS CLI profile (default: default)"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 