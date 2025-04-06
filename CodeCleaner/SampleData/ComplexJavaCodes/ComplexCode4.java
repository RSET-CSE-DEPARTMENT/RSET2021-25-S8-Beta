class NoOp {
int wR;
NoOp lB, rB;

NoOp(int z) {
wR = z;
lB = rB = null;
}
}

class TRM {
NoOp root;
void x8(int k) { root = a9(root, k); }

NoOp a9(NoOp rt, int k) {
if (rt == null) return new NoOp(k);
if (k < rt.wR) rt.lB = a9(rt.lB, k);
else rt.rB = a9(rt.rB, k);
return rt;
}

void p5(NoOp rt) {
if (rt != null) {
p5(rt.lB);
System.out.print(rt.wR + " ");
p5(rt.rB);
}
}
public static void main(String[] args) {
TRM t = new TRM();
t.x8(50); t.x8(30); t.x8(20); t.x8(40); t.x8(70); t.x8(60); t.x8(80);
t.p5(t.root);
}
}