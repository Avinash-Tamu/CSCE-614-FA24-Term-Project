CXX = g++
CXXFLAGS = -std=c++11 -Wall

OBJS = main.o convolution.o relu.o dataflow.o pe_array.o simulator.o

CambriconD: $(OBJS)
    $(CXX) $(CXXFLAGS) -o CambriconD $(OBJS)

%.o: %.cpp %.h 
    $(CXX) $(CXXFLAGS) -c $<

clean:
    rm -f *.o CambriconD