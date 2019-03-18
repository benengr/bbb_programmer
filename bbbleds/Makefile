src = $(wildcard *.cpp)
obj = $(src:.c=.o)
outdir = bin/
LDFLAGS =  -lpthread
CC=$(CROSS_COMPILE)g++
ledd: $(obj)
	mkdir -p $(outdir)
	$(CC) -o $(outdir)$@ $^ $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(obj)
	rm -rf $(outdir)*