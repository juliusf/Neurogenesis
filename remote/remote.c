#include <mpi.h>
#define WORKTAG     1
#define DIETAG     2
main(argc, argv)
int argc;
char *argv[];
{
    int         myrank;
    MPI_Init(&argc, &argv);   /* initialize MPI */
    MPI_Comm_rank(
    MPI_COMM_WORLD,   /* always use this */
    &myrank);      /* process rank, 0 thru N-1 */
    if (myrank == 0) {
        master(&argc, &argv);
    } else {
        slave();
    }
    MPI_Finalize();       /* cleanup MPI */
}

master(const int *argc, const char *argv[])
{
    int workPool[10] = {0,1,2,3,4,5,6,7,8,9};
    int next_work_element = 0;
    int workPoolSize = 10;

    int ntasks, rank, work;
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
        work = workPool[next_work_element]; /* get_next_work_request */
        next_work_element++;
        MPI_Send(&work,         /* message buffer */
        1,              /* one data item */
        MPI_INT,        /* data item is an integer */
        rank,           /* destination process rank */
        WORKTAG,        /* user chosen message tag */
        MPI_COMM_WORLD);/* always use this */
    }

/*
* Receive a result from any slave and dispatch a new work
* request work requests have been exhausted.
*/
    work = workPool[next_work_element];/* get_next_work_request */
    next_work_element++;
    while (next_work_element <= workPoolSize) {
        MPI_Recv(&result,       /* message buffer */
        1,              /* one data item */
        MPI_DOUBLE,     /* of type double real */
        MPI_ANY_SOURCE, /* receive from any sender */
        MPI_ANY_TAG,    /* any type of message */
        MPI_COMM_WORLD, /* always use this */
        &status);       /* received message info */
        MPI_Send(&work, 1, MPI_INT, status.MPI_SOURCE,
        WORKTAG, MPI_COMM_WORLD);
        work = workPool[next_work_element];
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

slave()
{
    double              result;
    int                 work;
    MPI_Status          status;
    for (;;) {
        MPI_Recv(&work, 1, MPI_INT, 0, MPI_ANY_TAG,
        MPI_COMM_WORLD, &status);
/*
* Check the tag of the received message.
*/
        if (status.MPI_TAG == DIETAG) {
            return;
        }
        result = 0;
        int world_rank;
        MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
        printf("workID: %i, rank: %i \n", work, world_rank);
        MPI_Send(&result, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }
}
