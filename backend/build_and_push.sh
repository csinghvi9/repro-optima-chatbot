#!/bin/bash
 
# ---- CONFIG ----
AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="628316596570"
REPO_NAME="ivfchatbot/backend"
LOCAL_IMAGE_NAME="indra-chatbot-backend"
TAG="latest"
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$TAG"
# ----------------
 
echo "🔐 Logging into AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
if [ $? -ne 0 ]; then
  echo "❌ ECR login failed"
  exit 1
fi
 
echo "🔨 Building Docker image: $LOCAL_IMAGE_NAME"
docker buildx build --no-cache --load -t $LOCAL_IMAGE_NAME .
 
 
echo "🏷️ Tagging image as: $ECR_URI"
docker tag $LOCAL_IMAGE_NAME:latest $ECR_URI
 
echo "📤 Pushing image to ECR..."
docker push $ECR_URI
 
echo "✅ Successfully pushed image to: $ECR_URI"