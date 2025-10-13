#!/usr/bin/env python3
"""
Verification script for altpg project

This script verifies that all components of altpg are properly installed
and working correctly.
"""

import sys
import subprocess

def check_import():
    """Check if altpg can be imported."""
    print("✓ Checking altpg import...")
    try:
        import altpg
        print(f"  ✅ altpg version {altpg.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Failed to import altpg: {e}")
        return False


def check_db_api():
    """Check DB-API 2.0 compliance."""
    print("\n✓ Checking DB-API 2.0 compliance...")
    try:
        import altpg
        
        # Check module attributes
        assert hasattr(altpg, 'apilevel'), "Missing apilevel"
        assert hasattr(altpg, 'threadsafety'), "Missing threadsafety"
        assert hasattr(altpg, 'paramstyle'), "Missing paramstyle"
        
        assert altpg.apilevel == "2.0", f"Wrong apilevel: {altpg.apilevel}"
        assert altpg.threadsafety == 2, f"Wrong threadsafety: {altpg.threadsafety}"
        assert altpg.paramstyle == "pyformat", f"Wrong paramstyle: {altpg.paramstyle}"
        
        print(f"  ✅ API Level: {altpg.apilevel}")
        print(f"  ✅ Thread Safety: {altpg.threadsafety}")
        print(f"  ✅ Parameter Style: {altpg.paramstyle}")
        return True
    except Exception as e:
        print(f"  ❌ DB-API 2.0 check failed: {e}")
        return False


def check_classes():
    """Check that required classes exist."""
    print("\n✓ Checking required classes...")
    try:
        import altpg
        
        required_classes = ['Connection', 'Cursor']
        for cls in required_classes:
            assert hasattr(altpg, cls), f"Missing class: {cls}"
            print(f"  ✅ {cls} class available")
        
        return True
    except Exception as e:
        print(f"  ❌ Class check failed: {e}")
        return False


def check_exceptions():
    """Check exception hierarchy."""
    print("\n✓ Checking exception hierarchy...")
    try:
        import altpg
        
        exceptions = [
            'DatabaseError',
            'IntegrityError',
            'ProgrammingError',
            'OperationalError',
            'InterfaceError'
        ]
        
        for exc in exceptions:
            assert hasattr(altpg, exc), f"Missing exception: {exc}"
            print(f"  ✅ {exc} available")
        
        # Check hierarchy
        assert issubclass(altpg.IntegrityError, altpg.DatabaseError)
        assert issubclass(altpg.ProgrammingError, altpg.DatabaseError)
        assert issubclass(altpg.OperationalError, altpg.DatabaseError)
        print(f"  ✅ Exception hierarchy correct")
        
        return True
    except Exception as e:
        print(f"  ❌ Exception check failed: {e}")
        return False


def check_connect():
    """Check connect function."""
    print("\n✓ Checking connect function...")
    try:
        import altpg
        
        assert hasattr(altpg, 'connect'), "Missing connect function"
        assert callable(altpg.connect), "connect is not callable"
        
        print(f"  ✅ connect() function available")
        return True
    except Exception as e:
        print(f"  ❌ Connect function check failed: {e}")
        return False


def check_sqlalchemy():
    """Check SQLAlchemy integration."""
    print("\n✓ Checking SQLAlchemy integration...")
    try:
        import altpg.sqlalchemy
        from altpg.sqlalchemy import AltpgDialect
        
        assert hasattr(AltpgDialect, 'driver'), "Missing driver attribute"
        assert AltpgDialect.driver == 'altpg', f"Wrong driver: {AltpgDialect.driver}"
        
        print(f"  ✅ SQLAlchemy dialect available")
        print(f"  ✅ Driver name: {AltpgDialect.driver}")
        return True
    except ImportError:
        print(f"  ⚠️  SQLAlchemy not installed (optional)")
        return True
    except Exception as e:
        print(f"  ❌ SQLAlchemy integration check failed: {e}")
        return False


def check_tests():
    """Check if tests can be run."""
    print("\n✓ Checking test suite...")
    try:
        result = subprocess.run(
            ['pytest', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  ✅ pytest available: {result.stdout.strip()}")
            
            # Try to run tests
            result = subprocess.run(
                ['pytest', 'tests/', '-v', '--tb=no'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Count passed tests
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'passed' in line:
                        print(f"  ✅ {line.strip()}")
                        break
                return True
            else:
                print(f"  ❌ Tests failed")
                print(result.stdout)
                return False
        else:
            print(f"  ⚠️  pytest not available (optional)")
            return True
    except FileNotFoundError:
        print(f"  ⚠️  pytest not installed (optional)")
        return True
    except Exception as e:
        print(f"  ❌ Test check failed: {e}")
        return False


def check_build():
    """Check if package can be built."""
    print("\n✓ Checking build capability...")
    try:
        result = subprocess.run(
            ['cargo', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  ✅ Rust/Cargo available: {result.stdout.strip()}")
        else:
            print(f"  ⚠️  Rust/Cargo not available (only needed for building)")
        
        result = subprocess.run(
            ['maturin', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  ✅ maturin available: {result.stdout.strip()}")
        else:
            print(f"  ⚠️  maturin not available (only needed for building)")
        
        return True
    except FileNotFoundError:
        print(f"  ⚠️  Build tools not installed (only needed for development)")
        return True
    except Exception as e:
        print(f"  ⚠️  Build check skipped: {e}")
        return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("altpg Verification Script")
    print("=" * 60)
    
    checks = [
        check_import,
        check_db_api,
        check_classes,
        check_exceptions,
        check_connect,
        check_sqlalchemy,
        check_tests,
        check_build,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n✅ All checks passed! altpg is ready to use.")
        return 0
    else:
        print("\n⚠️  Some checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
