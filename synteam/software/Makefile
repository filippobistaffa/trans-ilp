TARGET = syn_team_journal
CXXFLAGS = -ansi -O3 -fpermissive -std=c++17
CPLOBJS = Timer.o


SYSTEM     = x86-64_linux
LIBFORMAT  = static_pic
CPLEXROOT      = /opt/ibm/ILOG/CPLEX_Studio201
CPLEXDIR       = $(CPLEXROOT)/cplex
CONCERTDIR     = $(CPLEXROOT)/concert
CPOPTIMIZERDIR = $(CPLEXROOT)/cpoptimizer
GCC = gcc
CCC = g++
CCOPT = -m64 -O -fPIC -fexceptions -DNDEBUG -DIL_STD -std=c++17 -fpermissive -w
CPLEXBINDIR   = $(CPLEXDIR)/bin/$(BINDIST)
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

syn_team_journal: syn_team_journal.o $(CPLOBJS)
	$(CCC) $(CCFLAGS) syn_team_journal.o $(CPLOBJS) -o syn_team_journal $(CCLNFLAGS)

syn_team_journal.o: syn_team_journal.cpp
	$(CCC) -c $(CCFLAGS) syn_team_journal.cpp -o syn_team_journal.o 

clean:
	@rm -f *~ *.o ${TARGET} core
