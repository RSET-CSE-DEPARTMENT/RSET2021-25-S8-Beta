// SimpleCode4: Reverse a String
import java.util.Scanner;

public class SimpleCode4 {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.print("Enter a string: ");
String str = scanner.nextLine();
String reversed = new StringBuilder(str).reverse().toString();
System.out.println("Reversed String: " + reversed);
scanner.close();
}
}