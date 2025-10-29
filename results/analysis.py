import csv
import statistics

def analyze_results(filepath='measurements.csv'):
    """
    Analyzes the results from the measurements.csv file and prints a summary.
    """
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        print("Please ensure you have run the experiments using 'docker compose up' first.")
        return

    # Separate data by phase
    cold = [r for r in rows if r['phase'] == 'cold' and r['status'] == '200']
    warm = [r for r in rows if r['phase'] == 'warm' and r['status'] == '200']
    replay = [r for r in rows if r['phase'] == 'replay']

    print("--- Authentication Performance Analysis ---")

    def analyze_phase(data, name):
        if not data:
            print(f"\nNo successful data points found for {name}.")
            return None

        e2e = [float(r['end_to_end_ms']) for r in data]
        token_ex = [float(r['token_exchange_ms']) for r in data]
        dpop_sign = [float(r['dpop_sign_ms']) for r in data]
        server_verify = [float(r['server_verify_ms']) for r in data]

        mean_e2e = statistics.mean(e2e)
        print(f"\n{name} (n={len(data)}):")
        print(f"  - End-to-End Latency: {mean_e2e:.2f} ms (SD: {statistics.stdev(e2e):.2f})")
        print(f"    - Token Exchange:     {statistics.mean(token_ex):.2f} ms")
        print(f"    - DPoP Signing:       {statistics.mean(dpop_sign):.2f} ms")
        print(f"    - Server Verification:{statistics.mean(server_verify):.2f} ms")
        return mean_e2e

    cold_avg = analyze_phase(cold, "Cold Path (Full Token Exchange)")
    warm_avg = analyze_phase(warm, "Warm Path (Cached Token)")

    if cold_avg and warm_avg and warm_avg > 0:
        speedup = cold_avg / warm_avg
        print(f"\nCaching Speedup: {speedup:.1f}x")

    print("\n--- Security Validation ---")
    if len(replay) >= 2 and replay[0]['status'] == '200' and replay[1]['status'] == '403':
        print("✅ DPoP Replay Attack: Correctly REJECTED (200 OK -> 403 Forbidden)")
    else:
        print("❌ DPoP Replay Attack: FAILED VALIDATION")

if __name__ == '__main__':
    import os
    # Support running from both project root and results directory
    if os.path.exists('measurements.csv'):
        analyze_results('measurements.csv')
    elif os.path.exists('results/measurements.csv'):
        analyze_results('results/measurements.csv')
    else:
        print("Error: Cannot find measurements.csv")
        print("Please run from project root or results directory")