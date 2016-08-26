#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define WORKTAG     1
#define DIETAG     2
#define DIGEST_SIZE 32
#define BASE_PATH "/mnt/distsim/simulations/"
#define EXECUTE_COMMAND "/./run.sh"



void master(int num_sims, char *sims[])
{
    int next_work_element = 0;
    int workPoolSize = num_sims;
    
    int ntasks, rank;
    char* work = (char *) malloc(DIGEST_SIZE+1);
    ntasks = workPoolSize;
    int       result = 0; 
    printf("got %i simulation runs\n", workPoolSize);
    MPI_Status     status;
    MPI_Comm_size(
    MPI_COMM_WORLD,    /* always use this */
    &ntasks);          /* #processes in application */
    /*
    * Seed the slaves.
    */
    
    for (rank = 1; rank < ntasks; ++rank) {
        strncpy(work, sims[next_work_element], DIGEST_SIZE+1);
        next_work_element++;
	printf("%i/%i:starting job: %s on rank: %i\n", next_work_element, workPoolSize, work, rank);
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
        MPI_INT,     /* of type int*/
        MPI_ANY_SOURCE, /* receive from any sender */
        MPI_ANY_TAG,    /* any type of message */
        MPI_COMM_WORLD, /* always use this */
        &status);       /* received message info */
	printf("received exit code: %i from rank %i\n", result, status.MPI_SOURCE);
	printf("%i/%i: starting job: %s on rank: %i\n", next_work_element, workPoolSize, work, status.MPI_SOURCE);
        MPI_Send(work, DIGEST_SIZE+1, MPI_BYTE, status.MPI_SOURCE,
        WORKTAG, MPI_COMM_WORLD);
        if(next_work_element != workPoolSize)
            strcpy(work, sims[next_work_element]);
        next_work_element++;
    }
/*
* Receive results for outstanding work requests.
*/
    for (rank = 1; rank < ntasks; ++rank) {
        MPI_Recv(&result, 1, MPI_INT, MPI_ANY_SOURCE,
        MPI_ANY_TAG, MPI_COMM_WORLD, &status);
    	printf("received exit code: %i from rank %i\n", result, status.MPI_SOURCE);
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

    int result = 0;
    char*  work = (char *) malloc(DIGEST_SIZE+1);
    MPI_Status status;

    for (;;) {
        MPI_Recv(work, DIGEST_SIZE+1, MPI_BYTE, 0, MPI_ANY_TAG,
        MPI_COMM_WORLD, &status);
        /*
        * Check the tag of the received message.
        */

        if (status.MPI_TAG == DIETAG) {
            free(work);
            return;
        }

        int base_length = strlen(BASE_PATH);
        int command_length = strlen(EXECUTE_COMMAND);
	int work_length = strlen(work);
	
	if (isspace( (unsigned char) work[work_length -1 ])){
		work[work_length -1] = '\0';
	}

        char* execute_command = (char*) malloc(base_length + DIGEST_SIZE + command_length + 1);
        execute_command[0] = '\0';
        strcat(execute_command, BASE_PATH);
        strcat(execute_command, work);
        strcat(execute_command, EXECUTE_COMMAND);
        result = system (execute_command);
        free(execute_command);
        MPI_Send(&result, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    }
}

int get_num_sims(char *filename){
	FILE* fp = fopen(filename, "r");
 	int ch = 0;
	int lines = 0;
	if (fp == NULL){
		return 0;
	}
	
	while ((ch = fgetc(fp)) != EOF)
	{
		if (ch == '\n'){
			lines++;
		}
	}
	fclose(fp);
	return lines;
}
char** get_list_of_sims(int nr_of_sims, char* filename){
	FILE* fp = fopen(filename, "r");
	if (fp == NULL)
	{
		printf("Unable to open file Provided!");
		return NULL;
	}

	int line = 0;
	int ch = 0;
	int str_pos = 0;
	char** files = (char**) malloc(nr_of_sims * sizeof(char*));
	
	files[line] = (char*) malloc(DIGEST_SIZE + 1);
	while((ch = fgetc(fp)) != EOF){
		if (ch == '\n'){
			str_pos++;
			files[line][str_pos] = '\0';
			printf("%s\n", files[line]);
			line++;
			files[line] = (char*) malloc(DIGEST_SIZE +1);
			str_pos = 0;
		}else{
			files[line][str_pos] = ch;
			str_pos++;
		}
			
	}
	return files;	
}

int main(int argc, char *argv[])
{
    int         myrank;
    MPI_Init(&argc, &argv);   /* initialize MPI */
    MPI_Comm_rank(
    MPI_COMM_WORLD,   /* always use this */
    &myrank);      /* process rank, 0 thru N-1 */
   if (myrank == 0) {
	int num_sims = get_num_sims(argv[1]);
    	char** sims = get_list_of_sims(num_sims, argv[1]);
        master(num_sims, sims);
    } else {
        slave();
    }
    MPI_Finalize();       /* cleanup MPI */
}


