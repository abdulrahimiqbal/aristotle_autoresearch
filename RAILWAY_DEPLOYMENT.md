# Railway Deployment Guide - Aristotle Research Orchestrator

This guide covers deploying the Aristotle Research Orchestrator to Railway for 24/7 autonomous operation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Railway Deployment                            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ manager-273 │  │ manager-123 │  │ manager-181 │  ...         │
│  │  (Docker)   │  │  (Docker)   │  │  (Docker)   │               │
│  │ erdos273.db │  │ erdos123.db │  │ erdos181.db │               │
│  │ :8080/health│  │ :8080/health│  │ :8080/health│               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┴────────────────┘                     │
│                          │                                      │
│              ┌───────────▼───────────┐                        │
│              │      dashboard        │                        │
│              │   (Multi-tenant)      │                        │
│              │   Aggregates all DBs  │                        │
│              │       :8000           │                        │
│              └───────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

Each manager service:
- Runs in its own container with isolated SQLite database
- Has a health check endpoint at `:8080/health`
- Runs the `solve-env` command using environment variables
- Persists data to a Railway volume

The dashboard service:
- Connects to all problem databases (read-only)
- Provides a unified view at `:8000`
- Shows global summary + per-problem detail views

## Files Created

### Core Deployment Files
- `Dockerfile.manager` - Container for autonomous manager
- `Dockerfile.dashboard` - Container for unified dashboard
- `railway.yaml` - Railway service configuration
- `docker-compose.yml` - Local testing setup
- `deploy-to-railway.sh` - Automated deployment script

### New Python Modules
- `src/research_orchestrator/health_server.py` - Health check endpoint
- `src/research_orchestrator/manager_config.py` - Environment-based config
- `src/research_orchestrator/multi_tenant_dashboard.py` - Aggregated dashboard

### Modified Files
- `src/research_orchestrator/cli.py` - Added `solve-env` command
- `requirements.txt` - Updated dependencies

## Prerequisites

1. **Railway CLI** installed:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Docker** installed (for local testing)

3. **API Keys** set as environment variables:
   ```bash
   export MOONSHOT_API_KEY="your-key"
   export ARISTOTLE_API_KEY="your-key"
   ```

4. **Pre-initialized database** - The database must have the project already created:
   ```bash
   # Initialize locally first
   research-orchestrator start-campaign \
     --prompt "Erdős Problem 273: covering systems..." \
     --db ./erdos273.sqlite
   ```

## Deployment Steps

### Option 1: Automated (Recommended)

```bash
# Set your API keys
export MOONSHOT_API_KEY="sk-..."
export ARISTOTLE_API_KEY="..."

# Run the deployment script
./deploy-to-railway.sh
```

The script will:
1. Build Docker image locally
2. Push code to git
3. Deploy manager-273 service
4. Deploy dashboard service
5. Show you the URLs

### Option 2: Manual (More Control)

```bash
# 1. Push your code
git add -A
git commit -m "Railway deployment"
git push origin main

# 2. Create the manager service
railway service create manager-273

# 3. Set environment variables
railway vars --service manager-273 set "PROBLEM_NUMBER=273"
railway vars --service manager-273 set "PROJECT_ID=campaign-erdos-problem-273-d686516d"
railway vars --service manager-273 set "MOONSHOT_API_KEY=$MOONSHOT_API_KEY"
railway vars --service manager-273 set "ARISTOTLE_API_KEY=$ARISTOTLE_API_KEY"
railway vars --service manager-273 set "DATABASE_PATH=/data/erdos273.sqlite"
railway vars --service manager-273 set "LLM_MANAGER_MODE=gatekeeper"
railway vars --service manager-273 set "MAX_ACTIVE=3"
railway vars --service manager-273 set "TICK_INTERVAL=60"
railway vars --service manager-273 set "CONVERGENCE_THRESHOLD=0.95"
railway vars --service manager-273 set "HEALTH_PORT=8080"
railway vars --service manager-273 set "ENABLE_HEALTH_SERVER=true"

# 4. Create and mount volume
railway volume create data-273
railway volume mount data-273 --service manager-273 --mount-path "/data"

# 5. Deploy
railway up --service manager-273

# 6. Create dashboard service
railway service create dashboard
railway vars --service dashboard set 'DATABASE_CONFIG={"273":"/data/erdos273.sqlite"}'
railway vars --service dashboard set "PORT=8000"
railway volume mount data-273 --service dashboard --mount-path "/data"
railway up --service dashboard
```

## Local Testing

Test locally before deploying:

```bash
# Set API keys
export MOONSHOT_API_KEY="..."
export ARISTOTLE_API_KEY="..."

# Run with Docker Compose
docker-compose up

# In another terminal, check health
curl http://localhost:8080/health

# View dashboard
curl http://localhost:8000/global
```

## Environment Variables

### Manager Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROBLEM_NUMBER` | Yes | - | Problem ID (e.g., "273") |
| `PROJECT_ID` | Yes | - | Full project ID from database |
| `MOONSHOT_API_KEY` | Yes* | - | Moonshot AI API key |
| `ARISTOTLE_API_KEY` | Yes* | - | Aristotle provider API key |
| `DATABASE_PATH` | No | `/data/erdos{N}.sqlite` | SQLite database path |
| `WORKSPACE_PATH` | No | `/data/workspace` | Workspace directory |
| `MAX_ACTIVE` | No | `3` | Max concurrent experiments |
| `TICK_INTERVAL` | No | `60` | Seconds between ticks |
| `CONVERGENCE_THRESHOLD` | No | `0.95` | Target convergence |
| `LLM_MANAGER_MODE` | No | `gatekeeper` | LLM mode (gatekeeper/synthesis/none) |
| `HEALTH_PORT` | No | `8080` | Health check port |
| `ENABLE_HEALTH_SERVER` | No | `true` | Enable health endpoint |

*Required when using those features

### Dashboard Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_CONFIG` | Yes | `{}` | JSON map of problem→database paths |
| `PORT` | No | `8000` | HTTP port |

Example `DATABASE_CONFIG`:
```json
{
  "273": "/data/erdos273.sqlite",
  "123": "/data/erdos123.sqlite",
  "181": "/data/erdos181.sqlite",
  "44": "/data/erdos44.sqlite"
}
```

## API Endpoints

### Manager Health Check
```
GET http://manager-273.railway.app:8080/health

Response:
{
  "status": "healthy",
  "project_id": "campaign-erdos-problem-273-d686516d",
  "uptime_seconds": 3600,
  "active_experiments": 3,
  "queue_depth": 0,
  "last_tick_seconds_ago": 45,
  "llm_available": true,
  "tick_stale": false
}
```

### Dashboard Global View
```
GET http://dashboard.railway.app:8000/global
```

### Dashboard API
```
GET /api/problems              # List all problems
GET /api/global/summary        # Global summary
GET /api/problems/{id}/dashboard  # Problem detail
GET /api/problems/{id}/experiments  # Problem experiments
GET /api/health                # Dashboard health
```

## Adding More Problems

To add Erdős Problem 123:

1. **Initialize the database locally**:
   ```bash
   research-orchestrator start-campaign \
     --prompt "Erdős Problem 123: Complete sequences..." \
     --db ./erdos123.sqlite
   ```

2. **Update `deploy-to-railway.sh`**:
   ```bash
   PROBLEMS=("273" "123")
   PROJECT_IDS=("campaign-erdos-problem-273-d686516d" "campaign-erdos-problem-123")
   ```

3. **Re-run deployment**:
   ```bash
   ./deploy-to-railway.sh
   ```

## Monitoring

### View Logs
```bash
railway logs --service manager-273
railway logs --service dashboard
```

### Check Health
```bash
# Manager health
curl https://manager-273.your-domain.railway.app:8080/health

# Dashboard health
curl https://dashboard.your-domain.railway.app:8000/api/health
```

### Open Dashboard
```bash
railway open --service dashboard
```

## Troubleshooting

### "Database not found" Error
The database must be pre-initialized before deployment. Run `start-campaign` locally first.

### Health Check Failing
Check that `ENABLE_HEALTH_SERVER=true` is set and the container has started (60s startup period).

### No Data in Dashboard
Ensure the dashboard volume mounts are correct and the `DATABASE_CONFIG` JSON is valid.

### LLM Not Working
Verify `MOONSHOT_API_KEY` is set correctly. Check logs for authentication errors.

## Cost Considerations

Railway pricing is based on:
- **Compute**: ~$5-10/mo per manager service (running 24/7)
- **Storage**: ~$0.25/GB/mo for persistent volumes
- **Network**: Minimal for this use case

Example monthly cost for 4 problems + dashboard:
- 4 × manager services: ~$20-40
- 1 × dashboard service: ~$5-10
- Storage (4GB): ~$1
- **Total: ~$26-51/month**

## Next Steps / Future Enhancements

1. **Phase 2**: Add problems 123, 181, 44
2. **Cross-pollination**: Add `shared_lemmas` table for lemma sharing
3. **Alerting**: Slack/Discord notifications when problems stall
4. **Backup**: Automated database backups to S3
5. **Analytics**: Convergence rate tracking over time

## Support

For issues:
1. Check logs: `railway logs --service <name>`
2. Verify health: `curl <url>/health`
3. Review this guide and environment variables
