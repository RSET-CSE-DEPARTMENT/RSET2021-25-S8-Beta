// ComplexCode2: Custom Stack Implementation
class ZY_Stack {
private int arr[];
private int top;
private int cap;

ZY_Stack(int size) {
cap = size;
arr = new int[size];
top = -1;
}

void xP(int x) {
if (top == cap - 1) return;
arr[++top] = x;
}
int yP() {
if (top == -1) return -1;
return arr[top--];
}

public static void main(String args[]) {
ZY_Stack s = new ZY_Stack(5);
s.xP(10);
s.xP(20);
System.out.println(s.yP());
}
}