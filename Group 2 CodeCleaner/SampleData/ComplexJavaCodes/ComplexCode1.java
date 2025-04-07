// ComplexCode1: Matrix Multiplication
class XyZ1 {
static void zzA(int A[][], int B[][], int C[][], int N) {
for (int i = 0; i < N; i++)
for (int j = 0; j < N; j++)
for (int k = 0; k < N; k++)
C[i][j] += A[i][k] * B[k][j];
}

public static void main(String[] args) {
int A[][] = { {1, 2}, {3, 4} };
int B[][] = { {2, 0}, {1, 2} };
int N = 2;
int C[][] = new int[N][N];

zzA(A, B, C, N);

for (int i = 0; i < N; i++) {
for (int j = 0; j < N; j++)
System.out.print(C[i][j] + " ");
System.out.println();
}
}
}