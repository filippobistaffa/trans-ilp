#ifndef ORACLE_HPP_
#define ORACLE_HPP_

using namespace std;

#include <vector>
#include <string>
#include <map>

#include "oracle.h"

vector<struct Agent> cpp_read_agents(const char *filename);

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team, const struct Data data);

#endif /* ORACLE_HPP_ */
