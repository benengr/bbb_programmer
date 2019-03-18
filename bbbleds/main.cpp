#include <cstdio>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>

pthread_mutex_t state_lock;

enum States {
    DONE,
    ERROR,
    CYLON_1,
    CYLON_2,
    CYLON_3,
    CYLON_4,
    CYLON_5,
    CYLON_6
};

// This needs to be global becase
// it is set by signal callbacks.
States next = CYLON_1;

void do_state(States next) {    
    static States last = CYLON_1;
    if(next == last) return;
    last = next;
    switch(next) {
        case DONE:
            printf("Done\n");
        break;
        case ERROR:
            printf("Error\n");
        break;
        case CYLON_1:
            printf("1\n");
        break;
        case CYLON_2:
        case CYLON_6:
            printf("2\n");
        break;
        case CYLON_3:
        case CYLON_5:
            printf("3\n");
        break;
        case CYLON_4:
            printf("4\n");
        break;
    }
}

States getNextState(States current) {
    static int cylon_count = 0;
    switch(current) {
        case CYLON_1:        
            cylon_count++;
            if(cylon_count >= 4) {
                cylon_count = 0;
                return CYLON_2;
            }
        break;
        case CYLON_2:
        return CYLON_3;
        case CYLON_3:
        return CYLON_4;
        case CYLON_4:
            cylon_count++;
            if(cylon_count >= 4) {
                cylon_count = 0;
                return CYLON_5;
            }
        break;
        case CYLON_5:
        return CYLON_6;
        case CYLON_6:
        return CYLON_1;
        
    }
    return current;
}

void sig_handler(int signum) {
    std::printf("Received %d\n", signum);
    pthread_mutex_lock(&state_lock);
    switch(signum) {
        case SIGUSR1:
            next = DONE;
            break;
        case SIGUSR2:
            next = ERROR;
            break;
    }
    pthread_mutex_unlock(&state_lock);
}

int main() {
    int cylon_count = 1;
    signal(SIGUSR1, sig_handler);
    signal(SIGUSR2, sig_handler);

    while(1) {
        do_state(next);
        pthread_mutex_lock(&state_lock);
        next = getNextState(next);
        pthread_mutex_unlock(&state_lock);
        usleep(100000);
    }
}