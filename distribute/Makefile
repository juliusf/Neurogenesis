EXECS=distribute
MPICC?=mpicc
CFLAGS=-std=c99 -pedantic -Wall -Wextra -Werror -Wno-unused-function -Wno-unused-parameter -Wno-overlength-strings
CFLAGSDEBUG=-std=c99 -pedantic -Wall -Wextra -Werror -Wno-unused-function -Wno-unused-parameter -Wno-overlength-strings -g
all: ${EXECS}

distribute: distribute.c
	    ${MPICC} -o distribute distribute.c ${CFLAGS}

debug: distribute.c
		${MPICC} -o distribute distribute.c ${CFLAGSDEBUG}
clean:
	    rm ${EXECS}
