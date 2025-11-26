# Google Cloud Platform Deployment Guide

## Option 1: Cloud Run (Recommended - Serverless)

Cloud Run is the simplest way to deploy containers on GCP. It scales to zero
when not in use, so you only pay for actual usage.

### Prerequisites
- gcloud CLI installed and configured
- Docker installed locally
- GCP project with billing enabled

### Steps

1. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com
   ```

2. **Configure Docker for GCR**
   ```bash
   gcloud auth configure-docker
   ```

3. **Build and Push Docker Image**
   ```bash
   # Build image
   docker build -t gcr.io/<PROJECT_ID>/omnitech-support:latest .

   # Push to Container Registry
   docker push gcr.io/<PROJECT_ID>/omnitech-support:latest
   ```

4. **Create Secret for HF_TOKEN**
   ```bash
   echo -n "your_huggingface_token" | gcloud secrets create hf-token --data-file=-

   # Grant Cloud Run access to the secret
   gcloud secrets add-iam-policy-binding hf-token \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

5. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy omnitech-support \
     --image gcr.io/<PROJECT_ID>/omnitech-support:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 7860 \
     --memory 2Gi \
     --cpu 1 \
     --timeout 300 \
     --set-secrets HF_TOKEN=hf-token:latest
   ```

6. **Get the URL**
   ```bash
   gcloud run services describe omnitech-support --format='value(status.url)'
   ```

### Estimated Cost
- Cloud Run: Pay per request (~$0.00002400 per vCPU-second)
- Scales to zero = $0 when idle
- Container Registry: ~$0.10/GB/month

---

## Option 2: App Engine Flexible

For a more traditional PaaS experience with always-on instances.

### Steps

1. **Copy app.yaml to project root**
   ```bash
   cp gcp/app.yaml ../
   ```

2. **Update app.yaml port** (App Engine uses 8080)
   - Modify your app.py to use port 8080, or
   - Set GRADIO_SERVER_PORT=8080 in environment

3. **Deploy**
   ```bash
   gcloud app deploy
   ```

4. **Set Secrets** (via Console)
   - Go to App Engine > Settings > Environment Variables
   - Add HF_TOKEN

5. **Access App**
   ```bash
   gcloud app browse
   ```

### Estimated Cost
- App Engine Flex: ~$30-50/month minimum (always-on instance)

---

## Option 3: Google Kubernetes Engine (GKE)

For production workloads requiring Kubernetes.

```bash
# Create cluster
gcloud container clusters create omnitech-cluster --num-nodes=1

# Get credentials
gcloud container clusters get-credentials omnitech-cluster

# Create secret
kubectl create secret generic hf-token --from-literal=HF_TOKEN=your_token

# Deploy (create a k8s deployment yaml)
kubectl apply -f kubernetes-deployment.yaml
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| HF_TOKEN | HuggingFace API token | Yes |

## Troubleshooting

- **Container won't start**: Check Cloud Logging
- **Cold start too slow**: Increase min instances or use App Engine
- **Out of memory**: Increase memory limit in deployment

