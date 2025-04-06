// SimpleCode6: Palindrome Checker
import java.util.Scanner;

public class SimpleCode6 {
public static boolean isPalindrome(String str) {
return str.equals(new StringBuilder(str).reverse().toString());
}
    
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.print("Enter a string: ");
String input = scanner.nextLine();
System.out.println(input + " is " + (isPalindrome(input) ? "" : "not ") + "a palindrome.");
scanner.close();
}
}