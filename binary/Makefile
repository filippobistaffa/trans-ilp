TARGET = oracle
CXXFLAGS = -ansi -O3 -fpermissive -std=c++17


SYSTEM     = x86-64_linux
LIBFORMAT  = static_pic
ROOTDIR       = /opt/ibm/ILOG/CPLEX_Studio201
CPLEXDIR      = $(ROOTDIR)/cplex
CONCERTDIR    = $(ROOTDIR)/concert
CPOPTIMIZERDIR = $(ROOTDIR)/cpoptimizer
GCC = gcc
CCC = g++
CCOPT = -m64 -O -fPIC -fexceptions -DNDEBUG -DIL_STD -std=c++17 -fpermissive -w
CPLEXLIBDIR   = $(CPLEXDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CONCERTLIBDIR = $(CONCERTDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CPOPTIMIZERLIBDIR = $(CPOPTIMIZERDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CCLNFLAGS = -L$(CPLEXLIBDIR) -L$(CPOPTIMIZERLIBDIR) -lilocplex -lcplex -lcp -L$(CONCERTLIBDIR) -lconcert -lm -pthread -lpthread -ldl
CLNFLAGS  = -L$(CPLEXLIBDIR) -lcplex -lm -pthread -lpthread -ldl
CONCERTINCDIR = $(CONCERTDIR)/include
CPOPTIMIZERINCDIR = $(CPOPTIMIZERDIR)/include
CPLEXINCDIR   = $(CPLEXDIR)/include
CCFLAGS = $(CCOPT) -DCPLEX -I$(CPLEXINCDIR) -I$(CONCERTINCDIR) -I$(CPOPTIMIZERINCDIR)

all: ${TARGET}

oracle: oracle.cpp
	$(CCC) $(CCFLAGS) oracle.cpp -o oracle $(CCLNFLAGS)

clean:
	@rm oracle
