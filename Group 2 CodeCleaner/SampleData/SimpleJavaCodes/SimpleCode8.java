// SimpleCode8: Find GCD of Two Numbers
import java.util.Scanner;

public class SimpleCode8 {
public static int gcd(int a, int b) {
return (b == 0) ? a : gcd(b, a % b);
}

public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.print("Enter two numbers: ");
int a = scanner.nextInt();
int b = scanner.nextInt();
System.out.println("GCD of " + a + " and " + b + " is " + gcd(a, b));
scanner.close();
}
}