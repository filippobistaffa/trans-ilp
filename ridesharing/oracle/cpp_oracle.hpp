#ifndef ORACLE_HPP_
#define ORACLE_HPP_

// Macros
#define PTR(VAR) .VAR = &VAR

// Headers
#include <vector>
#include <cstring>

// Modules
#include "types.hpp"
#include "params.h"
#include "qos_type.hpp"
#include "coal_type.hpp"

#include "srvalue.hpp"
#include "qos.hpp"
#include "compute_value.hpp"

float cpp_oracle(const uint32_t s, const uint32_t *_c, const uint32_t n, const uint32_t *_reqs, const uint32_t *_steps, const uint32_t *_deltas, const float *_distance, const float *_time);

#endif /* ORACLE_HPP_ */
