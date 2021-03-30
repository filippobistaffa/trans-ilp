#ifndef ORACLE_HPP_
#define ORACLE_HPP_

using namespace std;

#include <vector>
#include <string>
#include <map>

#include "oracle.h"

void cpp_read_agents(const char *filename, struct Data data);

void cpp_read_task_competences(const char *filename, struct Data data);

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team, const struct Data data);

#endif /* ORACLE_HPP_ */
