#ifndef ILP_HPP_
#define ILP_HPP_

// Headers
#include <vector>   // vector
#include <utility>  // pair

// CPLEX
#include <ilcplex/ilocplex.h>

// Epsilon for float comparison
#define EPSILON 1e-2

// Maximum cardinality
#define K 5

// Number of zones
#define Z 63

// Enable solution output
#define PRINT_SOLUTION

// Types
typedef unsigned int req;
typedef float value;

struct coal {
	req c[K + 1];
	value w;
};

// Colours
#include "colours.h"

// Profiling
//#include <gperftools/profiler.h>
#define BREAKPOINT(MSG) do { puts(MSG); fflush(stdout); while (getchar() != '\n'); } while (0)

#endif /* ILP_HPP_ */
