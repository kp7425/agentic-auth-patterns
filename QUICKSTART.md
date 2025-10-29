# Quick Start Guide

Get the prototype running in under 5 minutes.

## Prerequisites Check

```bash
# Verify Docker
docker --version
# Required: Docker Engine 20.10+

# Verify Docker Compose
docker compose version
# Required: Docker Compose 2.0+

# Check available ports
lsof -i :8080  # Should be empty
lsof -i :8000  # Should be empty
```

## One-Command Start

```bash
# Clone repository
git clone https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype.git
cd agentic-auth-prototype

# Build and run everything
docker compose up --build
```

Wait for output:
```
orchestrator  | === Phase 1: Cold Start (20 iterations) ===
orchestrator  | === Phase 2: Warm Path (100 iterations) ===
orchestrator  | === Results saved to measurements.csv ===
```

## View Results

```bash
# In another terminal
cd agentic-auth-prototype
python3 results/analyze_for_paper.py
```

Expected output:
```
Cold Path: 52.2 ± 8.1 ms
Warm Path: 11.3 ± 4.2 ms
Speedup: 4.6x
✓ Replay prevention working!
```

## What's Running?

- **Keycloak** (http://localhost:8080): OAuth authorization server
  - Admin console: admin/admin
  - Realm: agentic-demo

- **Internal API** (http://localhost:8000): Protected resource server
  - Health check: http://localhost:8000/health

- **Orchestrator**: Runs experiments and exits

## Next Steps

1. **View data**: `cat results/measurements.csv`
2. **Generate LaTeX**: `python3 results/generate_latex.py`
3. **Read architecture**: See [README.md](README.md) for details
4. **Modify experiments**: Edit `orchestrator/experiments.py`

## Troubleshooting

### Keycloak takes too long

```bash
# Wait 60 seconds, then check
docker compose logs keycloak | grep "started"
```

### Port already in use

```bash
# Find and kill process
lsof -i :8080 | grep LISTEN
kill -9 <PID>
```

### Orchestrator fails immediately

```bash
# Check Keycloak health first
curl http://localhost:8080/health/ready
# Should return {"status":"UP"}
```

## Clean Up

```bash
# Stop everything
docker compose down

# Reset all data
docker compose down -v
```

## Support

Open an issue on GitLab or contact:
- Badal Bhushan: badalbhushan786@gmail.com
- Karthik Pappu: karthikp.pappu@trojans.dsu.edu
