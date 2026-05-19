#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://dclaw-secure-backend:8031}"

echo "==> Building backend image..."
docker build -t dclaw-secure-backend:local "$REPO_ROOT/backend"

echo "==> Building frontend image..."
docker build \
  --build-arg NEXT_PUBLIC_API_URL="" \
  --build-arg BACKEND_URL="$BACKEND_URL" \
  -t dclaw-secure-frontend:local \
  "$REPO_ROOT/frontend"

echo "==> Importing images into k3s containerd..."
docker save dclaw-secure-backend:local  | k3s ctr images import -
docker save dclaw-secure-frontend:local | k3s ctr images import -

echo "==> Applying k8s manifests..."
kubectl apply -f "$REPO_ROOT/k8s/secret.yaml"
kubectl apply -f "$REPO_ROOT/k8s/postgres.yaml"
kubectl apply -f "$REPO_ROOT/k8s/backend.yaml"
kubectl apply -f "$REPO_ROOT/k8s/frontend.yaml"

echo "==> Waiting for PostgreSQL to be ready..."
kubectl rollout status statefulset/dclaw-secure-postgres -n dclaw-core --timeout=120s

echo "==> Waiting for backend to be ready..."
kubectl rollout status deployment/dclaw-secure-backend -n dclaw-core --timeout=120s

echo "==> Waiting for frontend to be ready..."
kubectl rollout status deployment/dclaw-secure-frontend -n dclaw-core --timeout=120s

echo "==> Registering in dpanel app registry..."
kubectl apply -f "$REPO_ROOT/k8s/registry-patch.yaml"

echo ""
echo "✓ DClaw Secure deployed!"
echo "  Frontend: http://100.108.104.15:30031"
echo "  dpanel:   http://100.108.104.15:30300"
