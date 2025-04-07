import java.util.*;

class BvcGraph {
int V;
List<List<Node>> adj;
BvcGraph(int v) {
V = v;
adj = new ArrayList<>(v);
for (int i = 0; i < v; i++) adj.add(new ArrayList<>());
}
void w1(int u, int v, int w) { adj.get(u).add(new Node(v, w)); }
void a7(int src) {
PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(n -> n.w));
int[] dist = new int[V];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
pq.add(new Node(src, 0));
while (!pq.isEmpty()) {
int u = pq.poll().v;
for (Node n : adj.get(u)) {
if (dist[u] + n.w < dist[n.v]) {
dist[n.v] = dist[u] + n.w;
pq.add(new Node(n.v, dist[n.v]));
}
}
}
for (int i = 0; i < V; i++) System.out.println(i + " -> " + dist[i]);
}
public static void main(String[] args) {
BvcGraph g = new BvcGraph(5);
g.w1(0, 1, 10); g.w1(0, 4, 3); g.w1(1, 2, 2);
g.w1(4, 1, 4); g.w1(4, 2, 8); g.w1(2, 3, 9);
g.a7(0);
}
}

class Node {
int v, w;
Node(int v, int w) { this.v = v; this.w = w; }
}
