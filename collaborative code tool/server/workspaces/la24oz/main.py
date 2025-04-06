# file2.py
import file1

shared_variable = "Shared variable in file2"

def greet_from_file2():
    print("Hello from file2!")

if __name__ == "__main__":
    print("Running file2 directly")
    greet_from_file2()
    file1.greet_from_file1()