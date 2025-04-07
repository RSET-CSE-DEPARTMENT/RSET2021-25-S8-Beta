class KzzFib {
static int fibR(int n) {
if (n <= 1) return n;
return fibR(n - 1) + fibR(n - 2);
}
public static void main(String args[]) {
int n = 10;
for (int i = 0; i < n; i++) System.out.print(fibR(i) + " ");
}
}
