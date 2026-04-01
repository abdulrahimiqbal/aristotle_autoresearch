#!/bin/bash
# Deploy Aristotle Research Orchestrator to Railway
# Phase 1: Single problem (273) - Phase 2: Multi-problem

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROBLEMS=("273")
PROJECT_IDS=("campaign-erdos-problem-273-d686516d")

# Enable dashboard deployment
DEPLOY_DASHBOARD=true

# Optional: Add more problems for Phase 2
# PROBLEMS=("273" "123" "181" "44")
# PROJECT_IDS=(
#     "campaign-erdos-problem-273-d686516d"
#     "campaign-erdos-problem-123"
#     "campaign-erdos-problem-181"
#     "campaign-erdos-problem-44"
# )

echo -e "${GREEN}Deploying Aristotle Research Orchestrator to Railway...${NC}"
echo ""

# Check prerequisites
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Error: Railway CLI not found${NC}"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found${NC}"
    exit 1
fi

# Check env vars
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo -e "${YELLOW}Warning: MOONSHOT_API_KEY not set${NC}"
fi

if [ -z "$ARISTOTLE_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ARISTOTLE_API_KEY not set${NC}"
fi

# Step 1: Build and test locally
echo -e "${GREEN}Step 1: Building Docker image locally...${NC}"
docker build -f Dockerfile.manager -t research-orchestrator:test .
echo -e "${GREEN}✓ Local build successful${NC}"
echo ""

# Step 2: Push code to git
echo -e "${GREEN}Step 2: Pushing code to repository...${NC}"
git add -A
git commit -m "Deploy: Railway multi-tenant Phase 1" || true
git push origin main || true
echo -e "${GREEN}✓ Code pushed${NC}"
echo ""

# Step 3: Deploy each manager service
echo -e "${GREEN}Step 3: Deploying manager services...${NC}"

for i in "${!PROBLEMS[@]}"; do
    problem=${PROBLEMS[$i]}
    project_id=${PROJECT_IDS[$i]}
    service_name="manager-$problem"

    echo -e "${YELLOW}Deploying $service_name...${NC}"

    # Create service if not exists (ignore error if exists)
    railway service create "$service_name" 2>/dev/null || true

    # Set environment variables
    echo "  Setting environment variables..."
    railway vars --service "$service_name" set "PROBLEM_NUMBER=$problem"
    railway vars --service "$service_name" set "PROJECT_ID=$project_id"
    railway vars --service "$service_name" set "DATABASE_PATH=/data/erdos$problem.sqlite"
    railway vars --service "$service_name" set "WORKSPACE_PATH=/data/workspace"
    railway vars --service "$service_name" set "MAX_ACTIVE=3"
    railway vars --service "$service_name" set "TICK_INTERVAL=60"
    railway vars --service "$service_name" set "CONVERGENCE_THRESHOLD=0.95"
    railway vars --service "$service_name" set "PROVIDER_NAME=aristotle-cli"
    railway vars --service "$service_name" set "LLM_MANAGER_MODE=gatekeeper"
    railway vars --service "$service_name" set "HEALTH_PORT=8080"
    railway vars --service "$service_name" set "ENABLE_HEALTH_SERVER=true"

    # Set secret env vars if available
    if [ -n "$MOONSHOT_API_KEY" ]; then
        railway vars --service "$service_name" set "MOONSHOT_API_KEY=$MOONSHOT_API_KEY"
    fi
    if [ -n "$ARISTOTLE_API_KEY" ]; then
        railway vars --service "$service_name" set "ARISTOTLE_API_KEY=$ARISTOTLE_API_KEY"
    fi

    # Create volume if not exists
    echo "  Ensuring volume exists: data-$problem..."
    railway volume create "data-$problem" 2>/dev/null || true

    # Attach volume to service
    railway volume mount "data-$problem" --service "$service_name" --mount-path "/data"

    # Deploy
    echo "  Deploying..."
    railway up --service "$service_name"

    echo -e "${GREEN}✓ $service_name deployed${NC}"
    echo ""
done

# Step 4: Deploy dashboard
echo ""
if [ "$DEPLOY_DASHBOARD" = true ]; then
    echo -e "${GREEN}Step 4: Deploying unified dashboard...${NC}"

    railway service create "dashboard" 2>/dev/null || true

    # Build database config
    db_config="{"
    first=true
    for problem in "${PROBLEMS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            db_config+=","
        fi
        db_config+="\"$problem\":\"/data/erdos$problem.sqlite\""
    done
    db_config+="}"

    railway vars --service "dashboard" set "DATABASE_CONFIG=$db_config"
    railway vars --service "dashboard" set "PORT=8000"

    # Mount all data volumes as read-only
    for problem in "${PROBLEMS[@]}"; do
        railway volume mount "data-$problem" --service "dashboard" --mount-path "/data" || true
    done

    railway up --service "dashboard"
    echo -e "${GREEN}✓ Dashboard deployed${NC}"
fi

# Step 5: Show status
echo ""
echo -e "${GREEN}Step 5: Deployment complete!${NC}"
echo ""
echo "Deployed services:"
for problem in "${PROBLEMS[@]}"; do
    service_name="manager-$problem"
    url=$(railway service --service "$service_name" | grep "Domain" | awk '{print $2}' || echo "pending...")
    echo "  - $service_name: $url"
done

if [ "$DEPLOY_DASHBOARD" = true ]; then
    dashboard_url=$(railway service --service "dashboard" | grep "Domain" | awk '{print $2}' || echo "pending...")
    echo "  - dashboard: $dashboard_url"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Monitor logs: railway logs --service manager-273"
echo "2. Check health: curl https://<domain>/health"
echo "3. View dashboard: railway open"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
