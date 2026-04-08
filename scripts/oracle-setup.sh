#!/bin/bash
# ==============================================================================
# Oracle Cloud Always-Free VM Setup Script
# Run this on a fresh Oracle Linux 8 / Ubuntu 22.04 ARM instance
# ==============================================================================

set -e

echo "=== INVESTOR Backend Setup for Oracle Cloud ARM VM ==="

# --- 1. Install Docker ---
echo "Installing Docker..."
if command -v docker &> /dev/null; then
    echo "Docker already installed: $(docker --version)"
else
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "Docker installed. You may need to log out and back in for group changes."
fi

# --- 2. Install Ollama (optional, for LLM analysis) ---
echo ""
echo "Installing Ollama..."
if command -v ollama &> /dev/null; then
    echo "Ollama already installed"
else
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama installed."
fi

# --- 3. Create data directory ---
echo ""
echo "Creating data directory..."
sudo mkdir -p /data/investor
sudo chown $USER:$USER /data/investor

# --- 4. Clone the repo ---
echo ""
echo "Cloning repository..."
if [ -d "/home/$USER/investor" ]; then
    echo "Repository already exists, pulling latest..."
    cd /home/$USER/investor && git pull
else
    cd /home/$USER
    git clone https://github.com/ISTANBULBEKLE/investor.git
fi

# --- 5. Build Docker image ---
echo ""
echo "Building Docker image (this may take 5-10 minutes)..."
cd /home/$USER/investor/backend
docker build -t investor-backend .

# --- 6. Create .env file ---
echo ""
if [ ! -f "/data/investor/.env" ]; then
    echo "Creating .env from template..."
    cp .env.production.example /data/investor/.env
    echo ""
    echo "!!! IMPORTANT: Edit /data/investor/.env with your production values !!!"
    echo "  nano /data/investor/.env"
else
    echo ".env already exists at /data/investor/.env"
fi

# --- 7. Start the backend ---
echo ""
echo "Starting backend container..."
docker stop investor-backend 2>/dev/null || true
docker rm investor-backend 2>/dev/null || true

docker run -d \
    --name investor-backend \
    --restart unless-stopped \
    -p 8000:8000 \
    -v /data/investor:/app/data \
    --env-file /data/investor/.env \
    --add-host=host.docker.internal:host-gateway \
    investor-backend

echo ""
echo "=== Backend started! ==="
echo "  Health check: curl http://localhost:8000/health"
echo "  Logs: docker logs investor-backend --tail 50"
echo ""

# --- 8. Pull Ollama model ---
echo "Pulling Mistral model for Ollama (optional, ~4GB)..."
echo "Run: ollama pull mistral"
echo ""

# --- 9. Train ML models ---
echo "To train ML models, run:"
echo "  docker exec investor-backend python -m scripts.train_models --days 365"
echo ""

echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit /data/investor/.env with your Resend API key, email, etc."
echo "2. Run: ollama pull mistral"
echo "3. Run: docker exec investor-backend python -m scripts.train_models"
echo "4. Open firewall port 8000: sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT"
echo "5. Deploy frontend to Vercel with BACKEND_URL=http://YOUR_VM_IP:8000"
