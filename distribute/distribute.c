#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WORKTAG     1
#define DIETAG     2
#define DIGEST_SIZE 32
#define BASE_PATH "/tmp/distSim/simulations/"
#define EXECUTE_COMMAND "/./run.sh"



void master(int argc, char *argv[])
{
    int next_work_element = 0;
    int workPoolSize = argc -1;

    int ntasks, rank;
    char* work = (char *) malloc(DIGEST_SIZE+1);
    ntasks = workPoolSize;
    double       result;
    MPI_Status     status;
    MPI_Comm_size(
    MPI_COMM_WORLD,    /* always use this */
    &ntasks);          /* #processes in application */
    /*
    * Seed the slaves.
    */
    for (rank = 1; rank < ntasks; ++rank) {
        strncpy(work, argv[next_work_element + 1], DIGEST_SIZE+1);
        next_work_element++;
        MPI_Send(work,         /* message buffer */
        DIGEST_SIZE+1,              /* one data item */
        MPI_CHAR,        /* data item is an integer */
        rank,           /* destination process rank */
        WORKTAG,        /* user chosen message tag */
        MPI_COMM_WORLD);/* always use this */
    }

/*
* Receive a result from any slave and dispatch a new work
* request work requests have been exhausted.
*/
    while (next_work_element <= workPoolSize) {
        MPI_Recv(&result,       /* message buffer */
        1,              /* one data item */
        MPI_DOUBLE,     /* of type double real */
        MPI_ANY_SOURCE, /* receive from any sender */
        MPI_ANY_TAG,    /* any type of message */
        MPI_COMM_WORLD, /* always use this */
        &status);       /* received message info */
        MPI_Send(work, DIGEST_SIZE+1, MPI_BYTE, status.MPI_SOURCE,
        WORKTAG, MPI_COMM_WORLD);
        if(next_work_element != workPoolSize)
            strcpy(work, argv[next_work_element + 1]);
        next_work_element++;
    }
/*
* Receive results for outstanding work requests.
*/
    for (rank = 1; rank < ntasks; ++rank) {
        MPI_Recv(&result, 1, MPI_DOUBLE, MPI_ANY_SOURCE,
        MPI_ANY_TAG, MPI_COMM_WORLD, &status);
    }
/*
* Tell all the slaves to exit.
*/
    for (rank = 1; rank < ntasks; ++rank) {
        MPI_Send(0, 0, MPI_INT, rank, DIETAG, MPI_COMM_WORLD);
    }
}

void slave()
{

    double result = 0;
    char*  work = (char *) malloc(DIGEST_SIZE+1);
    MPI_Status status;

    for (;;) {
        MPI_Recv(work, DIGEST_SIZE+1, MPI_BYTE, 0, MPI_ANY_TAG,
        MPI_COMM_WORLD, &status);
        /*
        * Check the tag of the received message.
        */

        if (status.MPI_TAG == DIETAG) {
            return;
        }

        int base_length = strlen(BASE_PATH);
        int command_length = strlen(EXECUTE_COMMAND);

        char* execute_command = (char*) malloc(base_length + DIGEST_SIZE + command_length + 1);
        execute_command[0] = '\0';
        strcat(execute_command, BASE_PATH);
        strcat(execute_command, work);
        strcat(execute_command, EXECUTE_COMMAND);
        result = system (execute_command);
        free(execute_command);
        MPI_Send(&result, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }
}

int main(int argc, char *argv[])
{
    int         myrank;
    MPI_Init(&argc, &argv);   /* initialize MPI */
    MPI_Comm_rank(
    MPI_COMM_WORLD,   /* always use this */
    &myrank);      /* process rank, 0 thru N-1 */
    if (myrank == 0) {
        master(argc, argv);
    } else {
        slave();
    }
    MPI_Finalize();       /* cleanup MPI */
}
