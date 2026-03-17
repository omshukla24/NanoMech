#!/bin/bash
# NanoMech - Automated Google Cloud Deployment Script
# Created for Gemini Live Agent Challenge 2026
# #GeminiLiveAgentChallenge

set -e

# ==========================================
# CONFIGURATION — edit these
# ==========================================
PROJECT_ID="your-google-cloud-project-id"
REGION="us-central1"
SERVICE_NAME="nanomech"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "=================================="
echo "  NanoMech Cloud Deployment"
echo "  Google Cloud Run"
echo "=================================="

# Step 1 — Authenticate
echo "[1/5] Authenticating with Google Cloud..."
gcloud auth configure-docker

# Step 2 — Set project
echo "[2/5] Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Step 3 — Build container image
echo "[3/5] Building Docker image..."
gcloud builds submit --tag $IMAGE_NAME

# Step 4 — Deploy to Cloud Run
echo "[4/5] Deploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY

# Step 5 — Get service URL
echo "[5/5] Deployment complete!"
echo "=================================="
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format "value(status.url)"
echo "=================================="
echo "NanoMech deployed successfully!"
