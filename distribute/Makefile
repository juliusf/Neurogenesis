EXECS=distribute
MPICC?=mpicc
CFLAGS=-std=c99 -pedantic -Wall -Wextra -Werror -Wno-unused-function -Wno-unused-parameter -Wno-overlength-strings
all: ${EXECS}

distribute: distribute.c
	    ${MPICC} -o distribute distribute.c ${CFLAGS}

clean:
	    rm ${EXECS}
