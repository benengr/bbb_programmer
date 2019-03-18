src = $(wildcard *.cpp)
obj = $(src:.c=.o)
outdir = bin/
LDFLAGS =  -lpthread
deploydir= ../initramfs/bin/
CC=g++
CROSS_COMPILE ?= arm-linux-gnueabihf-

ledd: $(obj)
	mkdir -p $(outdir)
	$(CC) -o $(outdir)$@ $^ $(LDFLAGS)
	$(CROSS_COMPILE)$(CC) -o $(deploydir)$@ $^ $(LDFLAGS)
.PHONY: clean
clean:
	rm -f $(obj)
	rm -rf $(outdir)*