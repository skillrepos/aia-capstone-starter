# Azure Deployment Guide

## Option 1: Azure Container Apps (Recommended - Serverless)

Container Apps is Azure's serverless container platform. It scales to zero
and provides built-in load balancing and HTTPS.

### Prerequisites
- Azure CLI installed and logged in (`az login`)
- Docker installed locally
- Azure subscription

### Steps

1. **Create Resource Group**
   ```bash
   az group create --name omnitech-rg --location eastus
   ```

2. **Create Container Registry**
   ```bash
   az acr create --resource-group omnitech-rg --name omnitechacr --sku Basic
   az acr login --name omnitechacr
   ```

3. **Build and Push Docker Image**
   ```bash
   # Build image
   docker build -t omnitech-support .

   # Tag for ACR
   docker tag omnitech-support omnitechacr.azurecr.io/omnitech-support:latest

   # Push to ACR
   docker push omnitechacr.azurecr.io/omnitech-support:latest
   ```

4. **Create Container Apps Environment**
   ```bash
   az containerapp env create \
     --name omnitech-env \
     --resource-group omnitech-rg \
     --location eastus
   ```

5. **Deploy Container App**
   ```bash
   az containerapp create \
     --name omnitech-support \
     --resource-group omnitech-rg \
     --environment omnitech-env \
     --image omnitechacr.azurecr.io/omnitech-support:latest \
     --registry-server omnitechacr.azurecr.io \
     --target-port 7860 \
     --ingress external \
     --cpu 1.0 \
     --memory 2.0Gi \
     --min-replicas 0 \
     --max-replicas 10 \
     --secrets hf-token=<YOUR_HF_TOKEN> \
     --env-vars HF_TOKEN=secretref:hf-token
   ```

6. **Get the URL**
   ```bash
   az containerapp show \
     --name omnitech-support \
     --resource-group omnitech-rg \
     --query properties.configuration.ingress.fqdn
   ```

### Estimated Cost
- Container Apps: Pay per vCPU-second (~$0.000024/vCPU-second)
- Scales to zero = minimal cost when idle
- ACR Basic: ~$5/month

---

## Option 2: Azure App Service (Web App for Containers)

For a traditional PaaS experience with always-on instances.

### Steps

1. **Create App Service Plan**
   ```bash
   az appservice plan create \
     --name omnitech-plan \
     --resource-group omnitech-rg \
     --is-linux \
     --sku B1
   ```

2. **Create Web App**
   ```bash
   az webapp create \
     --resource-group omnitech-rg \
     --plan omnitech-plan \
     --name omnitech-support \
     --deployment-container-image-name omnitechacr.azurecr.io/omnitech-support:latest
   ```

3. **Configure Container Registry**
   ```bash
   az webapp config container set \
     --name omnitech-support \
     --resource-group omnitech-rg \
     --docker-registry-server-url https://omnitechacr.azurecr.io \
     --docker-registry-server-user omnitechacr \
     --docker-registry-server-password <ACR_PASSWORD>
   ```

4. **Set Environment Variables**
   ```bash
   az webapp config appsettings set \
     --resource-group omnitech-rg \
     --name omnitech-support \
     --settings WEBSITES_PORT=7860 HF_TOKEN=<YOUR_TOKEN>
   ```

5. **Access App**
   ```bash
   az webapp browse --name omnitech-support --resource-group omnitech-rg
   ```

### Estimated Cost
- App Service B1: ~$13/month

---

## Option 3: Azure Kubernetes Service (AKS)

For production workloads requiring Kubernetes.

```bash
# Create AKS cluster
az aks create \
  --resource-group omnitech-rg \
  --name omnitech-aks \
  --node-count 1 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group omnitech-rg --name omnitech-aks

# Create secret and deploy
kubectl create secret generic hf-token --from-literal=HF_TOKEN=your_token
kubectl apply -f kubernetes-deployment.yaml
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| HF_TOKEN | HuggingFace API token | Yes |
| WEBSITES_PORT | Port for App Service (7860) | For App Service |

## Troubleshooting

- **Container won't start**: Check Azure Monitor logs
- **Registry auth failed**: Ensure ACR admin user is enabled or use managed identity
- **Port not accessible**: Verify WEBSITES_PORT and ingress configuration
