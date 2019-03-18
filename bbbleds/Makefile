src = $(wildcard *.c)
obj = $(src:.c=.o)
outdir = bin/
LDFLAGS = 

ledd: $(obj)
	mkdir -p $(outdir)
	$(CC) -o $(outdir)$@ $^ $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(obj)
	rm -rf $(outdir)*