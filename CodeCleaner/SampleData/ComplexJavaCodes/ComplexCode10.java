import java.util.*;

class UuMap {
public static void main(String args[]) {
HashMap<String, Integer> m = new HashMap<>();
m.put("A", 10); m.put("B", 20); m.put("C", 30);
for (Map.Entry<String, Integer> entry : m.entrySet())
System.out.println(entry.getKey() + " " + entry.getValue());
m.remove("B");
System.out.println("After removal: " + m);
}
}
