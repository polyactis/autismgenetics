target = 
cpp_target = CalculateAlleleFrequency

CFLAGS = -fopenmp

all: $(target) $(cpp_target)

.c.o:
	-gcc $(CFLAGS) -c $< -o $@ 

.cc.o:
	-g++ $(CFLAGS) -c $< -o $@

$(target):	%:	%.o
	-gcc $(CFLAGS) $< -o $@

$(cpp_target):	%:	%.o
	-g++ $(CFLAGS) $< -o $@

clean:
	-rm *.o *~ $(target) $(cpp_target)
