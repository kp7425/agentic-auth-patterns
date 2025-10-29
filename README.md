# Agentic AI Authentication Prototype

**Empirical validation of authentication protocol composition for agentic AI systems**

This repository contains the prototype implementation used to validate authentication mechanisms in the paper:

> **"A Conceptual Framework for Authentication in Agentic AI Ecosystems: Protocol Analysis and Taxonomy"**
> Badal Bhushan, Karthik Pappu, Akashay Mittal

## Overview

This prototype demonstrates **Pattern 3** (Agent-to-Internal-Service) authentication from our five-pattern taxonomy, implementing:

- **OAuth 2.0** for initial authentication
- **Token Exchange (RFC 8693)** for delegation with user+agent context
- **DPoP (RFC 9449)** for sender-constrained tokens with replay prevention

### Key Findings

Our measurements show:
- **Cold-path latency**: 52.22ms (±8.08ms) - includes token acquisition and exchange
- **Warm-path latency**: 11.32ms (±4.22ms) - with token caching
- **Speedup**: 4.6× improvement through caching
- **DPoP overhead**: <1ms for ECDSA P-256 signing
- **Replay prevention**: Validated via JTI nonce cache

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Docker Network                         │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Keycloak    │◄────────│ Orchestrator │                 │
│  │  26.2        │  OAuth2 │  (Agent)     │                 │
│  │              │  Token  │              │                 │
│  │  Port: 8080  │  Exch   │  - Get token │                 │
│  └──────────────┘         │  - Exchange  │                 │
│                           │  - Gen DPoP  │                 │
│                           │  - Measure   │                 │
│                           └───────┬──────┘                  │
│                                   │                         │
│                                   │ DPoP-bound              │
│                                   │ Request                 │
│                                   ▼                         │
│                           ┌──────────────┐                  │
│                           │ Internal API │                  │
│                           │              │                  │
│                           │ - Verify JWT │                  │
│                           │ - Verify DPoP│                  │
│                           │ - Check JTI  │                  │
│                           │ - Measure    │                  │
│                           │              │                  │
│                           │ Port: 8000   │                  │
│                           └──────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Keycloak Authorization Server
- **Version**: 26.2
- **Purpose**: OAuth 2.0 provider with native RFC 8693 Token Exchange support
- **Configuration**: Realm with pre-configured clients for orchestrator and API

### 2. Orchestrator (Agent Simulator)
- **Language**: Python 3
- **Purpose**: Simulates an agentic orchestrator performing:
  - OAuth 2.0 client credentials grant
  - RFC 8693 token exchange for delegation
  - DPoP proof generation (ECDSA P-256)
  - Performance measurement

### 3. Internal API
- **Language**: Python 3 (Flask)
- **Purpose**: Protected resource server that:
  - Verifies OAuth access tokens
  - Validates DPoP proofs (RFC 9449)
  - Enforces JTI nonce replay prevention
  - Measures server-side verification time

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB available RAM
- 2GB available disk space
- Ports 8080 and 8000 available

## Quick Start

### 1. Clone Repository

```bash
git clone https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype.git
cd agentic-auth-prototype
```

### 2. Build Containers

```bash
docker compose build
```

**Expected output:**
```
[+] Building 45.2s (24/24) FINISHED
 => [keycloak internal] load build definition
 => [orchestrator internal] load build definition
 => [internal-api internal] load build definition
```

### 3. Start Services

```bash
docker compose up -d keycloak internal-api
```

**Wait for Keycloak to be ready** (~30 seconds):

```bash
# Check Keycloak health
curl http://localhost:8080/health/ready

# Expected output:
{"status":"UP","checks":[...]}
```

### 4. Run Experiments

```bash
docker compose up orchestrator
```

**Expected output:**
```
=== Phase 1: Cold Start (20 iterations) ===
Cold iteration 1/20...
Cold iteration 2/20...
...

=== Phase 2: Warm Path (100 iterations) ===
Warm iteration 1/100...
...

=== Phase 3: Replay Attack Test ===
First request: HTTP 200
Replay request: HTTP 403

=== Results saved to measurements.csv ===
```

### 5. View Results

```bash
# Check results file
ls -lh results/measurements.csv

# Preview first 10 rows
head -10 results/measurements.csv

# Analyze statistics
python3 results/analyze.py
```

## Results Analysis

The `results/` directory contains:

- **`measurements.csv`**: Raw per-request measurements with columns:
  - `phase`: cold/warm/replay
  - `iteration`: request number
  - `token_exchange_ms`: Token exchange time (or 0 if cached)
  - `dpop_sign_ms`: DPoP proof generation time
  - `api_call_ms`: Network + server verification time
  - `server_verify_ms`: Server-side verification time
  - `end_to_end_ms`: Total client-side latency
  - `status`: HTTP response code

- **`analyze.py`**: Statistical analysis script
- **`generate_latex.py`**: LaTeX table generator for paper

### Sample Analysis Output

```bash
python3 results/analyze.py
```

```
=== Cold Path ===
Token Exchange: 31.6 ± 1.4 ms
DPoP Sign: 0.7 ± 0.3 ms
Server Verify: 5.5 ± 2.4 ms
End-to-End: 52.2 ± 8.1 ms

=== Warm Path ===
Token Exchange: 0.0 ± 0.0 ms (cached)
DPoP Sign: 0.9 ± 0.4 ms
Server Verify: 6.4 ± 2.3 ms
End-to-End: 11.3 ± 4.2 ms

=== Speedup ===
Cold: 52.2 ms
Warm: 11.3 ms
Speedup: 4.6x

=== Replay Test ===
First request: HTTP 200
Replay request: HTTP 403
✓ Replay prevention working!
```

## Protocol Validation

### Token Exchange Verification

To verify that Keycloak is performing actual RFC 8693 token exchange:

```bash
# Inspect exchanged token claims
docker compose exec orchestrator python3 -c "
from orchestrator import Orchestrator
import jwt

orch = Orchestrator()
subject_token, _ = orch.get_user_token()
exchanged_token, _ = orch.exchange_token(subject_token)

# Decode without verification to inspect claims
claims = jwt.decode(exchanged_token, options={'verify_signature': False})
print('Subject:', claims.get('sub'))
print('Actor:', claims.get('act'))
print('Audience:', claims.get('aud'))
"
```

**Expected output:**
```
Subject: service-account-orchestrator
Actor: {...}
Audience: internal-api
```

### DPoP Validation

DPoP proofs are validated for:
- ✅ Correct `typ` header (`dpop+jwt`)
- ✅ ECDSA P-256 signature verification
- ✅ HTTP method binding (`htm`)
- ✅ HTTP URI binding (`htu`)
- ✅ Access token hash binding (`ath`)
- ✅ JTI uniqueness (replay prevention)

## Configuration

### Keycloak Realm

Pre-configured realm: `agentic-demo`

**Clients:**
- `orchestrator`: Client credentials flow with Token Exchange enabled
- `internal-api`: Resource server (bearer-only)

**Admin Console:**
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
orchestrator:
  environment:
    KEYCLOAK_URL: http://keycloak:8080
    INTERNAL_API_URL: http://internal-api:8000
    CLIENT_ID: orchestrator
    CLIENT_SECRET: orchestrator-secret
    REALM: agentic-demo
```

## Reproducing Paper Results

### Table II: Performance Measurements

```bash
# Run experiments
docker compose up orchestrator

# Generate LaTeX table
python3 results/generate_latex.py > paper_table.tex
```

**Output:**
```latex
\begin{table}[t]
\centering
\caption{Measured authentication overhead...}
\label{tab:performance}
\small
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Operation} & \textbf{Cold Path} & \textbf{Warm Path} \\
\midrule
Token Exchange & 31.64 $\pm$ 1.37 & 0.00 \\
DPoP Generation (Client) & 0.68 $\pm$ 0.31 & 0.87 $\pm$ 0.39 \\
Server Verification & 5.54 $\pm$ 2.41 & 6.36 $\pm$ 2.31 \\
\midrule
\textbf{Total End-to-End} & \textbf{52.22 $\pm$ 8.08} & \textbf{11.32 $\pm$ 4.22} \\
\bottomrule
\end{tabular}
\end{table}
```

## Project Structure

```
agentic-auth-prototype/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── docker-compose.yml           # Service orchestration
├── .gitignore                   # Git ignore patterns
│
├── keycloak/
│   ├── Dockerfile              # Keycloak container build
│   ├── realm-export.json       # Pre-configured realm
│   └── README.md               # Keycloak setup notes
│
├── orchestrator/
│   ├── Dockerfile              # Orchestrator container build
│   ├── requirements.txt        # Python dependencies
│   ├── orchestrator.py         # Main orchestrator logic
│   ├── experiments.py          # Experiment runner
│   └── README.md               # Orchestrator documentation
│
├── internal-api/
│   ├── Dockerfile              # API container build
│   ├── requirements.txt        # Python dependencies
│   ├── api.py                  # Flask API server
│   ├── dpop_verify.py          # DPoP verification logic
│   ├── jti_cache.py            # Replay prevention cache
│   └── README.md               # API documentation
│
├── results/
│   ├── measurements.csv        # Experimental data (generated)
│   ├── analyze.py              # Statistical analysis script
│   ├── generate_latex.py       # LaTeX table generator
│   └── README.md               # Results documentation
│
└── docs/
    ├── ARCHITECTURE.md         # System architecture details
    ├── PROTOCOLS.md            # Protocol specifications
    └── TROUBLESHOOTING.md      # Common issues and solutions
```

## Troubleshooting

### Issue: Keycloak won't start

```bash
# Check logs
docker compose logs keycloak

# Solution: Increase wait time or restart
docker compose restart keycloak
```

### Issue: Token Exchange fails

```bash
# Verify Keycloak configuration
docker compose exec keycloak \
  curl -s http://localhost:8080/realms/agentic-demo/.well-known/openid-configuration \
  | jq '.grant_types_supported'

# Should include: "urn:ietf:params:oauth:grant-type:token-exchange"
```

### Issue: DPoP verification fails

Common causes:
- **Clock skew**: Ensure system time is synchronized
- **URL mismatch**: Check `htu` claim matches request URL
- **Token hash mismatch**: Verify `ath` calculation

```bash
# Check orchestrator logs
docker compose logs orchestrator

# Check API logs
docker compose logs internal-api
```

### Issue: Port conflicts

```bash
# Check if ports are in use
lsof -i :8080  # Keycloak
lsof -i :8000  # Internal API

# Solution: Stop conflicting services or change ports in docker-compose.yml
```

## Cleaning Up

```bash
# Stop all services
docker compose down

# Remove volumes (resets Keycloak data)
docker compose down -v

# Remove built images
docker compose down --rmi all
```

## Extending the Prototype

### Adding SPIFFE/SPIRE

To implement full Pattern 3 with SPIFFE workload identity:

1. Add SPIRE server and agent containers
2. Replace OAuth client credentials with SPIFFE SVIDs
3. Modify token exchange to use SPIFFE identity as actor

See `docs/SPIFFE_INTEGRATION.md` for details.

### Adding More Patterns

- **Pattern 1 (User-to-Agent)**: Add OIDC authentication flow
- **Pattern 4 (Agent-to-External-API)**: Add external OAuth provider
- **Pattern 5 (Cross-Domain)**: Add second Keycloak instance for federation

## Performance Notes

### Test Environment

All measurements conducted on:
- **CPU**: Intel i7-9700K
- **RAM**: 32GB
- **OS**: Ubuntu 22.04 (via Docker Desktop)
- **Network**: Docker bridge (localhost)

### Expected Variance

- **Cold path**: ±15% variance due to JVM warmup and network jitter
- **Warm path**: ±30% variance (smaller absolute values more sensitive)
- **DPoP signing**: <1ms (highly stable, cryptographic operation)

### Production Considerations

Real-world deployments will differ:
- **Network latency**: Add 10-50ms for datacenter round-trips
- **Authorization server load**: May increase token exchange time
- **Concurrent agents**: Test scalability under load
- **Hardware acceleration**: ECDSA can use hardware crypto

## Security Considerations

⚠️ **This is a research prototype, not production-ready code.**

### Known Limitations

- **No TLS**: All communication over HTTP (use TLS in production)
- **Weak secrets**: Default credentials (rotate in production)
- **In-memory cache**: JTI cache lost on restart (use Redis/distributed cache)
- **No rate limiting**: Vulnerable to DoS (add rate limiting)
- **No monitoring**: Add observability for production

### Production Checklist

- [ ] Enable TLS for all communication
- [ ] Use strong, rotated credentials
- [ ] Implement distributed JTI cache
- [ ] Add rate limiting and throttling
- [ ] Set up monitoring and alerting
- [ ] Implement proper logging with audit trails
- [ ] Review and harden Keycloak configuration
- [ ] Perform security audit and penetration testing

## Citation

If you use this prototype in your research, please cite:

```bibtex
@inproceedings{bhushan2025agentic,
  title={A Conceptual Framework for Authentication in Agentic AI Ecosystems:
         Protocol Analysis and Taxonomy},
  author={Bhushan, Badal and Pappu, Karthik and Mittal, Akashay},
  booktitle={[Conference Name]},
  year={2025}
}
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contact

- **Badal Bhushan**: badalbhushan786@gmail.com
- **Karthik Pappu**: karthikp.pappu@trojans.dsu.edu
- **Akashay Mittal**: amittal18886@ucumberlands.edu

## Acknowledgments

- SPIFFE/SPIRE community for workload identity specifications
- OAuth and OpenID Connect communities for authentication standards
- Keycloak project for open-source authorization server
- Anthropic Claude for development assistance

## References

- [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749) - OAuth 2.0 Authorization Framework
- [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693) - OAuth 2.0 Token Exchange
- [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449) - OAuth 2.0 Demonstrating Proof of Possession (DPoP)
- [SPIFFE Specification](https://github.com/spiffe/spiffe)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
