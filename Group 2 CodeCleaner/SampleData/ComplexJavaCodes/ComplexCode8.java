import java.util.*;

class AxxGraph {
private int V;
private LinkedList<Integer> adj[];
AxxGraph(int v) {
V = v;
adj = new LinkedList[v];
for (int i = 0; i < v; i++) adj[i] = new LinkedList<>();
}
void addX(int v, int w) { adj[v].add(w); }
void bfsY(int s) {
boolean visited[] = new boolean[V];
LinkedList<Integer> queue = new LinkedList<>();
visited[s] = true;
queue.add(s);
while (!queue.isEmpty()) {
s = queue.poll();
System.out.print(s + " ");
for (int n : adj[s]) {
if (!visited[n]) {
visited[n] = true;
queue.add(n);
}
}
}
}
public static void main(String args[]) {
AxxGraph g = new AxxGraph(4);
g.addX(0, 1); g.addX(0, 2); g.addX(1, 2);
g.addX(2, 0); g.addX(2, 3); g.addX(3, 3);
g.bfsY(2);
}
}
