src = $(wildcard *.cpp)
obj = $(src:.c=.o)
outdir = bin/
LDFLAGS = 
CC=$(CROSS_COMPILE)gcc
ledd: $(obj)
	mkdir -p $(outdir)
	$(CC) -o $(outdir)$@ $^ $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(obj)
	rm -rf $(outdir)*