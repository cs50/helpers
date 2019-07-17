foo: foo.c
	clang -ggdb3 -O0 -std=c11 -Wall -Werror -Wshadow foo.c -lcs50 -lm -o foo

