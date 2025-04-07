class RtyList {
static class Node {
int data;
Node next;
Node(int d) { data = d; next = null; }
}
Node head;
void fD(int newData) {
Node newNode = new Node(newData);
newNode.next = head;
head = newNode;
}
void dY() {
Node temp = head;
while (temp != null) {
System.out.print(temp.data + " ");
temp = temp.next;
}
}
public static void main(String args[]) {
RtyList llist = new RtyList();
llist.fD(1); llist.fD(2); llist.fD(3);
llist.dY();
}
}
