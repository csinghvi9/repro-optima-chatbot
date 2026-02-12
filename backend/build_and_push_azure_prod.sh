#!/bin/bash

# Set these values
ACR_NAME="iivfaiacr01"                       # ACR name (without .azurecr.io)
IMAGE_NAME="prod-backend"         # Your image name
IMAGE_TAG="latest"                        # Tag (can be 'latest' or a version number like v1.0.0)

# Build full registry URL
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
FULL_IMAGE_NAME="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

# Log in to Azure and ACR
echo "🔐 Logging in to Azure..."
az login

echo "🔐 Logging in to ACR..."
az acr login --name $ACR_NAME

# Build the Docker image
echo "🐳 Building Docker image: $FULL_IMAGE_NAME ..."
docker build -t $FULL_IMAGE_NAME .

# Push the image to ACR
echo "📤 Pushing image to ACR..."
docker push $FULL_IMAGE_NAME

echo "✅ Image pushed successfully: $FULL_IMAGE_NAME"
