#include <stdio.h>

int main(void) {
  int x = 2;
  do {
    int x = 28;
    x++;
  } while (x < 30);
  printf("%d\n", x);
}
