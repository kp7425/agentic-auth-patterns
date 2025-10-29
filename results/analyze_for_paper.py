import csv
import statistics

# Load data
with open('measurements.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Separate phases
cold = [r for r in rows if r['phase'] == 'cold' and r['status'] == '200']
warm = [r for r in rows if r['phase'] == 'warm' and r['status'] == '200']

def calc_stats(data, field):
    """Calculate mean and standard deviation"""
    values = [float(r[field]) for r in data]
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0
    return mean, stdev

print("=" * 70)
print("LATEX TABLE DATA FOR PAPER")
print("=" * 70)

# Token Exchange
cold_exchange_mean, cold_exchange_std = calc_stats(cold, 'token_exchange_ms')
warm_exchange_mean, warm_exchange_std = calc_stats(warm, 'token_exchange_ms')

# DPoP Generation (client-side)
cold_dpop_mean, cold_dpop_std = calc_stats(cold, 'dpop_sign_ms')
warm_dpop_mean, warm_dpop_std = calc_stats(warm, 'dpop_sign_ms')

# Server Verification (total server time)
cold_server_mean, cold_server_std = calc_stats(cold, 'server_verify_ms')
warm_server_mean, warm_server_std = calc_stats(warm, 'server_verify_ms')

# End-to-End Total
cold_e2e_mean, cold_e2e_std = calc_stats(cold, 'end_to_end_ms')
warm_e2e_mean, warm_e2e_std = calc_stats(warm, 'end_to_end_ms')

# Calculate speedup
speedup = cold_e2e_mean / warm_e2e_mean if warm_e2e_mean > 0 else 0

print("\n--- Raw Statistics ---")
print(f"Cold samples: {len(cold)}")
print(f"Warm samples: {len(warm)}")
print(f"\nToken Exchange:")
print(f"  Cold: {cold_exchange_mean:.2f} ± {cold_exchange_std:.2f} ms")
print(f"  Warm: {warm_exchange_mean:.2f} ± {warm_exchange_std:.2f} ms")
print(f"\nDPoP Generation:")
print(f"  Cold: {cold_dpop_mean:.2f} ± {cold_dpop_std:.2f} ms")
print(f"  Warm: {warm_dpop_mean:.2f} ± {warm_dpop_std:.2f} ms")
print(f"\nServer Verification:")
print(f"  Cold: {cold_server_mean:.2f} ± {cold_server_std:.2f} ms")
print(f"  Warm: {warm_server_mean:.2f} ± {warm_server_std:.2f} ms")
print(f"\nEnd-to-End Total:")
print(f"  Cold: {cold_e2e_mean:.2f} ± {cold_e2e_std:.2f} ms")
print(f"  Warm: {warm_e2e_mean:.2f} ± {warm_e2e_std:.2f} ms")
print(f"\nSpeedup: {speedup:.1f}x")

print("\n" + "=" * 70)
print("COPY-PASTE LATEX TABLE")
print("=" * 70)
print()

# Generate LaTeX table
print(r"\begin{table}[t]")
print(r"\centering")
print(r"\caption{Measured authentication overhead for agent-to-internal-service")
print(r"authentication. Values show mean latency in milliseconds with standard")
print(r"deviation.}")
print(r"\label{tab:performance}")
print(r"\small")
print(r"\begin{tabular}{@{}lcc@{}}")
print(r"\toprule")
print(r"\textbf{Operation} & \textbf{Cold Path} & \textbf{Warm Path} \\")
print(r"\midrule")

# Token Exchange
print(f"Token Exchange & {cold_exchange_mean:.2f} $\\pm$ {cold_exchange_std:.2f} & {warm_exchange_mean:.2f} \\\\")

# DPoP Generation
print(f"DPoP Generation (Client) & {cold_dpop_mean:.2f} $\\pm$ {cold_dpop_std:.2f} & {warm_dpop_mean:.2f} $\\pm$ {warm_dpop_std:.2f} \\\\")

# Server Verification
print(f"Server Verification & {cold_server_mean:.2f} $\\pm$ {cold_server_std:.2f} & {warm_server_mean:.2f} $\\pm$ {warm_server_std:.2f} \\\\")

print(r"\midrule")

# Total
print(f"\\textbf{{Total End-to-End}} & \\textbf{{{cold_e2e_mean:.2f} $\\pm$ {cold_e2e_std:.2f}}} & \\textbf{{{warm_e2e_mean:.2f} $\\pm$ {warm_e2e_std:.2f}}} \\\\")

print(r"\midrule")

# Speedup
print(f"\\textbf{{Speedup (vs. Cold)}} & \\textbf{{1.0$\\times$}} & \\textbf{{{speedup:.1f}$\\times$}} \\\\")

print(r"\bottomrule")
print(r"\end{tabular}")
print(r"\end{table}")

print("\n" + "=" * 70)
print("EXPLANATION OF NUMBERS")
print("=" * 70)
print(f"""
WHAT THESE NUMBERS MEAN:

1. Token Exchange (Cold: {cold_exchange_mean:.1f}ms, Warm: 0ms)
   - Cold: HTTP round-trip to Keycloak for RFC 8693 token exchange
   - Warm: Reusing cached token (no exchange needed)

2. DPoP Generation (Cold: {cold_dpop_mean:.1f}ms, Warm: {warm_dpop_mean:.1f}ms)
   - Client-side ECDSA P-256 signature generation
   - Both cold/warm generate fresh DPoP proof for each request

3. Server Verification (Cold: {cold_server_mean:.1f}ms, Warm: {warm_server_mean:.1f}ms)
   - JWT signature verification
   - DPoP proof verification
   - JTI cache check (replay prevention)

4. Total End-to-End (Cold: {cold_e2e_mean:.1f}ms, Warm: {warm_e2e_mean:.1f}ms)
   - Complete request latency from client start to response received
   - Cold path dominated by token exchange overhead
   - Warm path shows {speedup:.1f}x speedup through token caching

IMPORTANT CAVEAT:
- These numbers assume Keycloak 26.2 is performing REAL token exchange
- You need to verify exchanged tokens contain 'act' (actor) claims
- If Keycloak is NOT doing actual RFC 8693 exchange, these are just HTTP overhead
""")
