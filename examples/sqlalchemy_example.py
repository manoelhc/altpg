"""
SQLAlchemy integration example for altpg

This example demonstrates how to use altpg with SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for declarative models
Base = declarative_base()


# Define a simple model
class User(Base):
    """Example User model."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


def sqlalchemy_core_example():
    """Example using SQLAlchemy Core API."""
    print("SQLAlchemy Core API Example")
    print("-" * 40)
    
    # Create engine with altpg dialect
    # Note: Replace with your actual database credentials
    engine = create_engine(
        'postgresql+altpg://postgres:password@localhost/testdb',
        echo=True  # Enable SQL logging
    )
    
    try:
        # Execute raw SQL
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"PostgreSQL version: {version}")
            
            # Create table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    email VARCHAR(100)
                )
            """))
            conn.commit()
            
            # Insert data
            conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                {"name": "Alice", "email": "alice@example.com"}
            )
            conn.commit()
            
            # Query data
            result = conn.execute(text("SELECT * FROM users"))
            for row in result:
                print(f"User: {row}")
        
        print("SQLAlchemy Core example completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    print()


def sqlalchemy_orm_example():
    """Example using SQLAlchemy ORM."""
    print("SQLAlchemy ORM Example")
    print("-" * 40)
    
    # Create engine with altpg dialect
    engine = create_engine(
        'postgresql+altpg://postgres:password@localhost/testdb',
        echo=True
    )
    
    try:
        # Create tables
        Base.metadata.create_all(engine)
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create new users
        user1 = User(name="Bob", email="bob@example.com")
        user2 = User(name="Charlie", email="charlie@example.com")
        
        # Add and commit
        session.add(user1)
        session.add(user2)
        session.commit()
        
        # Query users
        users = session.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  {user}")
        
        # Filter query
        alice = session.query(User).filter_by(name="Alice").first()
        if alice:
            print(f"Found Alice: {alice}")
        
        # Update user
        if alice:
            alice.email = "alice.updated@example.com"
            session.commit()
            print(f"Updated Alice's email: {alice.email}")
        
        # Delete user
        # bob = session.query(User).filter_by(name="Bob").first()
        # if bob:
        #     session.delete(bob)
        #     session.commit()
        #     print("Deleted Bob")
        
        session.close()
        print("SQLAlchemy ORM example completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    print()


def connection_pool_example():
    """Example using SQLAlchemy connection pooling."""
    print("Connection Pool Example")
    print("-" * 40)
    
    from sqlalchemy.pool import QueuePool
    
    # Create engine with connection pool
    engine = create_engine(
        'postgresql+altpg://postgres:password@localhost/testdb',
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        echo=True
    )
    
    try:
        # Use multiple connections from pool
        with engine.connect() as conn1:
            result = conn1.execute(text("SELECT 1"))
            print(f"Connection 1: {result.fetchone()}")
        
        with engine.connect() as conn2:
            result = conn2.execute(text("SELECT 2"))
            print(f"Connection 2: {result.fetchone()}")
        
        print("Connection pool example completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    print()


def transaction_example():
    """Example using SQLAlchemy transactions."""
    print("Transaction Example")
    print("-" * 40)
    
    engine = create_engine(
        'postgresql+altpg://postgres:password@localhost/testdb',
        echo=True
    )
    
    try:
        # Begin transaction
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                {"name": "Dave", "email": "dave@example.com"}
            )
            # Transaction is automatically committed
        
        print("Transaction example completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("Transaction was rolled back")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("altpg SQLAlchemy Integration Examples")
    print("=" * 50)
    print()
    
    print("Note: The following examples require a running PostgreSQL instance.")
    print("Update the connection string to match your setup:")
    print("  postgresql+altpg://user:password@host/database")
    print()
    
    # Uncomment the examples you want to run:
    # sqlalchemy_core_example()
    # sqlalchemy_orm_example()
    # connection_pool_example()
    # transaction_example()
    
    print("To run these examples, uncomment them in the code.")
