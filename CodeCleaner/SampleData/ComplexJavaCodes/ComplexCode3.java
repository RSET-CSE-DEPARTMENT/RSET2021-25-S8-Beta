// ComplexCode3: Quick Sort Algorithm
class XYZ_QS {
static void xQS(int arr[], int low, int high) {
if (low < high) {
int pi = yP(arr, low, high);
xQS(arr, low, pi - 1);
xQS(arr, pi + 1, high);
}
}

static int yP(int arr[], int low, int high) {
int pivot = arr[high], i = low - 1;
for (int j = low; j < high; j++) {
if (arr[j] < pivot) {
i++;
int temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
}
}
int temp = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = temp;
return i + 1;
}

public static void main(String args[]) {
int arr[] = {10, 7, 8, 9, 1, 5};
xQS(arr, 0, arr.length - 1);
for (int num : arr) System.out.print(num + " ");
}
}