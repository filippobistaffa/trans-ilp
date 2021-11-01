.PHONY: all

ifndef OUT
OUT=./pg2
endif

CMP=g++ -std=c++11
WARN=-Wall -Wno-unused-result -Wno-deprecated-declarations -Wno-sign-compare -Wno-maybe-uninitialized -Wno-ignored-attributes -Wno-strict-aliasing -Wno-catch-value
OPTIM=-Ofast -march=native -funroll-loops -funsafe-loop-optimizations -falign-functions=16 -falign-loops=16 -fopenmp
NOOPTIM=-O0 -march=native -fopenmp
DBG=-g ${NOOPTIM}
PROF=-g -DWITHGPERFTOOLS ${OPTIM}

#CPLEXROOT=/opt/ibm/ILOG/CPLEX_Studio1271
ARCH=x86-64_linux

INC=-DIL_STD #-I${CPLEXROOT}/cplex/include -I${CPLEXROOT}/concert/include
#LDIR=-L${CPLEXROOT}/concert/lib/${ARCH}/static_pic -L${CPLEXROOT}/cplex/lib/${ARCH}/static_pic
LINK=-lpthread #-lconcert -lilocplex -lcplex -lboost_timer -lboost_iostreams

COBJSUBDIR=cobj
DEPSUBDIR=dep

ECHOCC=>&2 echo "[ CC ]"
ECHOLD=>&2 echo "[ LD ]"

ifeq ($(PROFILE),1)
OPT=${PROF}
LINK+=-lprofiler
else
OPT=${OPTIM} # Put desired optimisation level here
endif

define compilec
${ECHOCC} $(notdir $<) ;\
mkdir -p ${DEPSUBDIR} ;\
tmp=`mktemp` ;\
${CMP} ${DEFS} ${INC} -MM ${OPT} $< >> $$tmp ;\
if [ $$? -eq 0 ] ;\
then echo -n "${COBJSUBDIR}/" > ${DEPSUBDIR}/$(notdir $<).d ;\
cat $$tmp >> ${DEPSUBDIR}/$(notdir $<).d ;\
rm $$tmp ;\
mkdir -p ${COBJSUBDIR} ;\
cd ${COBJSUBDIR} ;\
${CMP} ${DEFS} -c ${INC} ${OPT} ${WARN} ../$< ;\
else \
ret=$$? ;\
rm $$tmp ;\
exit $$ret ;\
fi
endef

all: pg2
	@true

-include ${DEPSUBDIR}/*.d

pg2: ${COBJSUBDIR}/pg2.o ${COBJSUBDIR}/io.o
	@${ECHOLD} pg2
	@${CMP} ${OPT} ${LDIR} $^ ${LINK} -o ${OUT}

${COBJSUBDIR}/pg2.o: pg2.cpp
	@$(compilec)

${COBJSUBDIR}/io.o: io.cpp
	@$(compilec)

clean:
	@echo "Removing subdirectories..."
	@rm -rf ${COBJSUBDIR} ${DEPSUBDIR}
