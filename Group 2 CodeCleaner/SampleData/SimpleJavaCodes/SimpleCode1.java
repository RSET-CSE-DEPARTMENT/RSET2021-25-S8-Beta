// SimpleCode1: Basic Calculator
import java.util.Scanner;

public class SimpleCode1 {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.print("Enter two numbers: ");
int a = scanner.nextInt();
int b = scanner.nextInt();
System.out.println("Sum: " + (a + b));
System.out.println("Difference: " + (a - b));
System.out.println("Product: " + (a * b));
System.out.println("Quotient: " + (a / b));
scanner.close();
}
}