# module1.py

def greet(name):
    return f"Hello, {name}! Welcome to the Python importing demo."

# Importing function from module2.py
from module2 import farewell

if __name__ == "__main__":
    print(greet("Alice"))
    print(farewell("Alice"))