"""
Benchmark script for comparing altpg performance

This script provides basic benchmarking capabilities to compare
altpg with other PostgreSQL adapters like psycopg2.

Note: Requires a running PostgreSQL instance and psycopg2 for comparison.
"""

import time
import sys

# Try to import available drivers
drivers = {}

try:
    import altpg
    drivers['altpg'] = altpg
except ImportError:
    print("altpg not installed")

try:
    import psycopg2
    drivers['psycopg2'] = psycopg2
except ImportError:
    print("psycopg2 not installed (optional for comparison)")


def benchmark_connection(driver_name, driver_module, dsn, iterations=100):
    """Benchmark connection creation."""
    print(f"\nBenchmarking {driver_name} - Connection Creation")
    print("-" * 50)
    
    start = time.time()
    for _ in range(iterations):
        try:
            conn = driver_module.connect(dsn)
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000  # Convert to milliseconds
    
    print(f"Total time: {elapsed:.2f}s")
    print(f"Average per connection: {avg_time:.2f}ms")
    print(f"Connections per second: {iterations/elapsed:.2f}")
    
    return elapsed


def benchmark_simple_query(driver_name, driver_module, dsn, iterations=1000):
    """Benchmark simple SELECT queries."""
    print(f"\nBenchmarking {driver_name} - Simple SELECT Query")
    print("-" * 50)
    
    try:
        conn = driver_module.connect(dsn)
        cursor = conn.cursor()
        
        start = time.time()
        for _ in range(iterations):
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        elapsed = time.time() - start
        avg_time = (elapsed / iterations) * 1000  # Convert to milliseconds
        
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average per query: {avg_time:.3f}ms")
        print(f"Queries per second: {iterations/elapsed:.2f}")
        
        cursor.close()
        conn.close()
        
        return elapsed
    except Exception as e:
        print(f"Error: {e}")
        return None


def benchmark_insert(driver_name, driver_module, dsn, iterations=1000):
    """Benchmark INSERT operations."""
    print(f"\nBenchmarking {driver_name} - INSERT Operations")
    print("-" * 50)
    
    try:
        conn = driver_module.connect(dsn)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_test (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                text_value TEXT
            )
        """)
        
        # Clear existing data
        cursor.execute("TRUNCATE benchmark_test")
        conn.commit()
        
        start = time.time()
        for i in range(iterations):
            cursor.execute(
                "INSERT INTO benchmark_test (value, text_value) VALUES (%s, %s)",
                (i, f"test_value_{i}")
            )
        conn.commit()
        
        elapsed = time.time() - start
        avg_time = (elapsed / iterations) * 1000  # Convert to milliseconds
        
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average per insert: {avg_time:.3f}ms")
        print(f"Inserts per second: {iterations/elapsed:.2f}")
        
        # Cleanup
        cursor.execute("DROP TABLE benchmark_test")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return elapsed
    except Exception as e:
        print(f"Error: {e}")
        return None


def benchmark_transaction(driver_name, driver_module, dsn, iterations=100):
    """Benchmark transaction operations."""
    print(f"\nBenchmarking {driver_name} - Transaction Operations")
    print("-" * 50)
    
    try:
        start = time.time()
        for _ in range(iterations):
            conn = driver_module.connect(dsn)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
        
        elapsed = time.time() - start
        avg_time = (elapsed / iterations) * 1000  # Convert to milliseconds
        
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average per transaction: {avg_time:.2f}ms")
        print(f"Transactions per second: {iterations/elapsed:.2f}")
        
        return elapsed
    except Exception as e:
        print(f"Error: {e}")
        return None


def run_benchmarks(dsn):
    """Run all benchmarks for available drivers."""
    print("=" * 60)
    print("PostgreSQL Driver Benchmarks")
    print("=" * 60)
    print(f"\nDSN: {dsn}")
    print(f"Available drivers: {', '.join(drivers.keys())}")
    
    results = {}
    
    for driver_name, driver_module in drivers.items():
        print(f"\n{'=' * 60}")
        print(f"Testing {driver_name}")
        print("=" * 60)
        
        results[driver_name] = {}
        
        # Connection benchmark
        results[driver_name]['connection'] = benchmark_connection(
            driver_name, driver_module, dsn, iterations=50
        )
        
        # Simple query benchmark
        results[driver_name]['simple_query'] = benchmark_simple_query(
            driver_name, driver_module, dsn, iterations=500
        )
        
        # Insert benchmark
        # Note: Commented out as it modifies the database
        # results[driver_name]['insert'] = benchmark_insert(
        #     driver_name, driver_module, dsn, iterations=100
        # )
        
        # Transaction benchmark
        results[driver_name]['transaction'] = benchmark_transaction(
            driver_name, driver_module, dsn, iterations=50
        )
    
    # Print comparison
    print("\n" + "=" * 60)
    print("Benchmark Summary")
    print("=" * 60)
    
    for benchmark in ['connection', 'simple_query', 'transaction']:
        print(f"\n{benchmark.replace('_', ' ').title()}:")
        for driver_name in drivers.keys():
            if results[driver_name][benchmark]:
                print(f"  {driver_name:15s}: {results[driver_name][benchmark]:.3f}s")
    
    # Calculate speedup if we have both drivers
    if 'altpg' in results and 'psycopg2' in results:
        print("\nSpeedup (psycopg2 time / altpg time):")
        for benchmark in ['connection', 'simple_query', 'transaction']:
            if results['altpg'][benchmark] and results['psycopg2'][benchmark]:
                speedup = results['psycopg2'][benchmark] / results['altpg'][benchmark]
                print(f"  {benchmark.replace('_', ' ').title():25s}: {speedup:.2f}x")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dsn = sys.argv[1]
    else:
        # Default DSN - update with your credentials
        dsn = "host=localhost port=5432 user=postgres password=password dbname=testdb"
        print(f"Using default DSN: {dsn}")
        print("To use a different DSN, pass it as an argument:")
        print(f"  python {sys.argv[0]} 'host=... port=... user=... password=... dbname=...'")
    
    if not drivers:
        print("No drivers available. Please install altpg and/or psycopg2.")
        sys.exit(1)
    
    print("\nNote: This benchmark requires a running PostgreSQL instance.")
    print("Press Ctrl+C to cancel.\n")
    
    try:
        input("Press Enter to start benchmarks...")
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    try:
        run_benchmarks(dsn)
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted.")
    except Exception as e:
        print(f"\n\nError running benchmarks: {e}")
        import traceback
        traceback.print_exc()
