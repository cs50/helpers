int main(void) {
  int temp[10];
  for (int i = 0; i < 1000; i += 900) {
    int x = temp[i];
    (void) x;
  }
}
