EXECS=remote
MPICC?=mpicc

all: ${EXECS}

remote: remote.c
	    ${MPICC} -o remote remote.c

clean:
	    rm ${EXECS}
