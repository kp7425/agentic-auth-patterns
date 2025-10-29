import csv
import time
from orchestrator import Orchestrator

def run_experiments():
    """Run authentication experiments and collect measurements"""

    print("Starting authentication experiments...")
    orch = Orchestrator()

    # Wait for services to be ready
    print("Waiting for services...")
    time.sleep(5)

    results = []

    # Phase 1: Cold start (no cached token)
    print("\n=== Phase 1: Cold Start (20 iterations) ===")
    orch.cached_token = None  # Clear cache

    for i in range(20):
        print(f"Cold iteration {i+1}/20...")
        metrics = orch.run_request(use_cache=False)
        metrics['phase'] = 'cold'
        metrics['iteration'] = i + 1
        results.append(metrics)
        time.sleep(0.5)  # Brief pause between requests

    # Phase 2: Warm path (cached token)
    print("\n=== Phase 2: Warm Path (100 iterations) ===")

    for i in range(100):
        if i % 20 == 0:
            print(f"Warm iteration {i+1}/100...")
        metrics = orch.run_request(use_cache=True)
        metrics['phase'] = 'warm'
        metrics['iteration'] = i + 1
        results.append(metrics)
        time.sleep(0.1)  # Faster for warm path

    # Phase 3: Replay attack demonstration
    print("\n=== Phase 3: Replay Attack Test ===")

    # Get valid token and DPoP
    access_token = orch.cached_token
    dpop_proof, _ = orch.generate_dpop_proof(
        "GET",
        f"{orch.api_url}/api/resource",
        access_token
    )

    # First request (should succeed)
    print("Sending first request (should succeed)...")
    response1, _ = orch.call_api(access_token, dpop_proof)
    print(f"First request: HTTP {response1.status_code}")

    # Replay request (should fail)
    print("Replaying same DPoP proof (should fail)...")
    time.sleep(0.5)
    response2, _ = orch.call_api(access_token, dpop_proof)
    print(f"Replay request: HTTP {response2.status_code}")

    results.append({
        'phase': 'replay',
        'iteration': 1,
        'token_exchange_ms': 0,
        'dpop_sign_ms': 0,
        'api_call_ms': 0,
        'server_verify_ms': 0,
        'end_to_end_ms': 0,
        'status': response1.status_code
    })

    results.append({
        'phase': 'replay',
        'iteration': 2,
        'token_exchange_ms': 0,
        'dpop_sign_ms': 0,
        'api_call_ms': 0,
        'server_verify_ms': 0,
        'end_to_end_ms': 0,
        'status': response2.status_code
    })

    # Save results
    print("\n=== Saving Results ===")
    with open('/app/results/measurements.csv', 'w', newline='') as f:
        fieldnames = [
            'phase', 'iteration', 'token_exchange_ms', 'dpop_sign_ms',
            'api_call_ms', 'server_verify_ms', 'end_to_end_ms', 'status'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to measurements.csv ({len(results)} rows)")
    print("\n=== Experiments Complete ===")

    # Print summary
    cold_results = [r for r in results if r['phase'] == 'cold']
    warm_results = [r for r in results if r['phase'] == 'warm']

    if cold_results:
        avg_cold = sum(r['end_to_end_ms'] for r in cold_results) / len(cold_results)
        print(f"Cold path average: {avg_cold:.2f} ms")

    if warm_results:
        avg_warm = sum(r['end_to_end_ms'] for r in warm_results) / len(warm_results)
        print(f"Warm path average: {avg_warm:.2f} ms")

        if cold_results:
            speedup = avg_cold / avg_warm if avg_warm > 0 else 0
            print(f"Speedup: {speedup:.1f}x")

if __name__ == '__main__':
    run_experiments()
