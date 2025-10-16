"""
Performance benchmarks for altpg.

This module provides benchmarks to compare altpg performance with psycopg2.

To run benchmarks:
    python tests/test_benchmarks.py

Requirements:
    - Running PostgreSQL instance
    - psycopg2 installed: pip install psycopg2-binary
    - altpg installed
"""

import time
import sys

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Warning: psycopg2 not installed, skipping comparison benchmarks")

import altpg


# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'password',
    'dbname': 'testdb'
}


def benchmark_connect_disconnect(driver_name, connect_func, iterations=100):
    """Benchmark connection creation and closing."""
    start = time.time()
    for _ in range(iterations):
        try:
            conn = connect_func(**DB_PARAMS)
            conn.close()
        except Exception as e:
            print(f"Error in {driver_name}: {e}")
            return None
    elapsed = time.time() - start
    return elapsed


def benchmark_simple_query(driver_name, connect_func, iterations=1000):
    """Benchmark simple SELECT 1 queries."""
    try:
        conn = connect_func(**DB_PARAMS)
        cursor = conn.cursor()
        
        start = time.time()
        for _ in range(iterations):
            cursor.execute("SELECT 1")
            cursor.fetchone()
        elapsed = time.time() - start
        
        cursor.close()
        conn.close()
        return elapsed
    except Exception as e:
        print(f"Error in {driver_name}: {e}")
        return None


def benchmark_parameter_query(driver_name, connect_func, iterations=1000):
    """Benchmark parameterized queries."""
    try:
        conn = connect_func(**DB_PARAMS)
        cursor = conn.cursor()
        
        start = time.time()
        for i in range(iterations):
            cursor.execute("SELECT %s, %s, %s", (i, f"string_{i}", i * 1.5))
            cursor.fetchone()
        elapsed = time.time() - start
        
        cursor.close()
        conn.close()
        return elapsed
    except Exception as e:
        print(f"Error in {driver_name}: {e}")
        return None


def benchmark_large_result_set(driver_name, connect_func, rows=10000):
    """Benchmark fetching large result sets."""
    try:
        conn = connect_func(**DB_PARAMS)
        cursor = conn.cursor()
        
        start = time.time()
        cursor.execute(f"SELECT generate_series(1, {rows})")
        results = cursor.fetchall()
        elapsed = time.time() - start
        
        assert len(results) == rows, f"Expected {rows} rows, got {len(results)}"
        
        cursor.close()
        conn.close()
        return elapsed
    except Exception as e:
        print(f"Error in {driver_name}: {e}")
        return None


def benchmark_insert_performance(driver_name, connect_func, iterations=1000):
    """Benchmark INSERT performance."""
    try:
        conn = connect_func(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("DROP TABLE IF EXISTS benchmark_test")
        cursor.execute("""
            CREATE TABLE benchmark_test (
                id SERIAL PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)
        conn.commit()
        
        start = time.time()
        for i in range(iterations):
            cursor.execute(
                "INSERT INTO benchmark_test (name, value) VALUES (%s, %s)",
                (f"test_{i}", i)
            )
        conn.commit()
        elapsed = time.time() - start
        
        # Cleanup
        cursor.execute("DROP TABLE benchmark_test")
        conn.commit()
        
        cursor.close()
        conn.close()
        return elapsed
    except Exception as e:
        print(f"Error in {driver_name}: {e}")
        return None


def print_benchmark_results(name, altpg_time, psycopg2_time=None):
    """Print benchmark results with comparison."""
    print(f"\n{name}:")
    if altpg_time is not None:
        print(f"  altpg:    {altpg_time:.4f}s")
    else:
        print(f"  altpg:    FAILED")
    
    if psycopg2_time is not None:
        print(f"  psycopg2: {psycopg2_time:.4f}s")
        if altpg_time is not None and psycopg2_time > 0:
            speedup = psycopg2_time / altpg_time
            if speedup > 1:
                print(f"  altpg is {speedup:.2f}x faster")
            else:
                print(f"  altpg is {1/speedup:.2f}x slower")


def run_all_benchmarks():
    """Run all benchmark suites."""
    print("=" * 60)
    print("altpg Performance Benchmarks")
    print("=" * 60)
    
    # Connection/disconnection benchmark
    print("\n1. Connect/Disconnect Benchmark (100 iterations)")
    altpg_time = benchmark_connect_disconnect("altpg", altpg.connect, 100)
    psycopg2_time = None
    if PSYCOPG2_AVAILABLE:
        psycopg2_time = benchmark_connect_disconnect("psycopg2", psycopg2.connect, 100)
    print_benchmark_results("Connect/Disconnect", altpg_time, psycopg2_time)
    
    # Simple query benchmark
    print("\n2. Simple Query Benchmark (1000 iterations)")
    altpg_time = benchmark_simple_query("altpg", altpg.connect, 1000)
    psycopg2_time = None
    if PSYCOPG2_AVAILABLE:
        psycopg2_time = benchmark_simple_query("psycopg2", psycopg2.connect, 1000)
    print_benchmark_results("Simple Query", altpg_time, psycopg2_time)
    
    # Parameter query benchmark
    print("\n3. Parameterized Query Benchmark (1000 iterations)")
    altpg_time = benchmark_parameter_query("altpg", altpg.connect, 1000)
    psycopg2_time = None
    if PSYCOPG2_AVAILABLE:
        psycopg2_time = benchmark_parameter_query("psycopg2", psycopg2.connect, 1000)
    print_benchmark_results("Parameterized Query", altpg_time, psycopg2_time)
    
    # Large result set benchmark
    print("\n4. Large Result Set Benchmark (10000 rows)")
    altpg_time = benchmark_large_result_set("altpg", altpg.connect, 10000)
    psycopg2_time = None
    if PSYCOPG2_AVAILABLE:
        psycopg2_time = benchmark_large_result_set("psycopg2", psycopg2.connect, 10000)
    print_benchmark_results("Large Result Set", altpg_time, psycopg2_time)
    
    # Insert performance benchmark
    print("\n5. INSERT Performance Benchmark (1000 iterations)")
    altpg_time = benchmark_insert_performance("altpg", altpg.connect, 1000)
    psycopg2_time = None
    if PSYCOPG2_AVAILABLE:
        psycopg2_time = benchmark_insert_performance("psycopg2", psycopg2.connect, 1000)
    print_benchmark_results("INSERT Performance", altpg_time, psycopg2_time)
    
    print("\n" + "=" * 60)
    print("Benchmarks Complete")
    print("=" * 60)


if __name__ == "__main__":
    print("\nNote: These benchmarks require a running PostgreSQL instance")
    print("with database 'testdb' accessible with the credentials in DB_PARAMS\n")
    
    response = input("Do you have PostgreSQL running? (y/n): ")
    if response.lower() == 'y':
        run_all_benchmarks()
    else:
        print("\nPlease start PostgreSQL and create the test database:")
        print("  createdb testdb")
        print("\nThen run this script again.")
