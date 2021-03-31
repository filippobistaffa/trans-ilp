#ifndef PG2_HPP_
#define PG2_HPP_

// Enable stable sorting algorithm
//#define STABLE_SORT

// Select which PRNG
#define PRNG mt19937
//#define PRNG default_random_engine

// Headers
#include <sys/time.h>
#include <random>
#include <vector>
#include <set>

// OpenMP
#include <omp.h>

// Global timer
struct timeval t1;

// Modules
#include "types.hpp"
#include "params.h"
#include "qos_type.hpp"
#include "coal_type.hpp"

#include "io.hpp"
#include "colours.h"
#include "srvalue.hpp"
#include "qos.hpp"
#include "greedysquared.hpp"

// Profiling
//#include <gperftools/profiler.h>
#define BREAKPOINT(MSG) do { puts(MSG); fflush(stdout); while (getchar() != '\n'); } while (0)

#endif /* PG2_HPP_ */
