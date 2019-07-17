// Run valgrind with --leak-check=full 

#include <stdlib.h>

int main(void) {
  int *x = malloc(sizeof(int));
}
