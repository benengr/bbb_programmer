#include <cstdio>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include <fstream>
#include <string>

using namespace std;
pthread_mutex_t state_lock;

string paths[] = {
    "/sys/class/leds/beaglebone:green:heartbeat",
    "/sys/class/leds/beaglebone:green:mmc0",
    "/sys/class/leds/beaglebone:green:usr2",
    "/sys/class/leds/beaglebone:green:usr3"
};

const char * getPath(int id, string element) {
    string val = paths[id] + element;
    return val.c_str();
}

void setSingleLed(int id) {
    std::fstream fs;
    int ledIndex = 0;

    for(ledIndex = 0; ledIndex < 4; ledIndex++) {
        fs.open(getPath(ledIndex, "/trigger"), std::fstream::out);
        fs << "none";
        fs.close();

        fs.open(getPath(ledIndex, "/brightness"), std::fstream::out);
        if(ledIndex = id - 1) {
            fs << "1";
        } else {
            fs << "0";
        }
        fs.close();
    }
}

void setErrorState() {
    std::fstream fs;
    int ledIndex = 0;

    for(ledIndex = 0; ledIndex < 4; ledIndex++) {
        fs.open(getPath(ledIndex, "/trigger"), std::fstream::out);
        fs << "timer";
        fs.close();

        fs.open(getPath(ledIndex, "/delay_on"), std::fstream::out);
        fs << "40";        
        fs.close();

        fs.open(getPath(ledIndex, "/delay_off"), std::fstream::out);
        fs << "60";        
        fs.close();
    }
}

void setDoneState() {
    int ledIndex = 4;
    fstream fs;
    setSingleLed(ledIndex);

    fs.open(getPath(ledIndex, "/trigger"), std::fstream::out);
    fs << "timer";
    fs.close();

    fs.open(getPath(ledIndex, "/delay_on"), std::fstream::out);
    fs << "40";        
    fs.close();

    fs.open(getPath(ledIndex, "/delay_off"), std::fstream::out);
    fs << "60";        
    fs.close();

}

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
            setDoneState();
        break;
        case ERROR:
            setErrorState();
        break;
        case CYLON_1:
            setSingleLed(1);
        break;
        case CYLON_2:
        case CYLON_6:
            setSingleLed(2);
        break;
        case CYLON_3:
        case CYLON_5:
            setSingleLed(3);
        break;
        case CYLON_4:
            setSingleLed(4);
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