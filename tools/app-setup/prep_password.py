
import bcrypt
import argparse

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def main():
    parser = argparse.ArgumentParser(description='Hash a password using bcrypt')
    parser.add_argument('password', help='Password to hash')
    
    args = parser.parse_args()
    
    hashed = hash_password(args.password)
    print(hashed.decode('utf-8'))

if __name__ == "__main__":
    main()