// SimpleCode3: Prime Number Checker
import java.util.Scanner;

public class SimpleCode3 {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.print("Enter a number: ");
int num = scanner.nextInt();
boolean isPrime = num > 1;
for (int i = 2; i <= Math.sqrt(num); i++) {
if (num % i == 0) {
isPrime = false;
break;
}
}
System.out.println(num + " is " + (isPrime ? "a Prime Number" : "not a Prime Number"));
scanner.close();
}
}