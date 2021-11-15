#ifndef ORACLE_HPP_
#define ORACLE_HPP_

using namespace std;

#include <utility>
#include <vector>
#include <string>
#include <map>

#include <Python.h>
#include "oracle.h"

vector<struct Agent> cpp_read_agents(const char *filename);

vector<struct Agent> cpp_sample_agents(size_t n, size_t seed);

pair<vector<string>, struct Task_type> cpp_read_task_competences(const char *filename);

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team, const struct Data data);

void cpp_remove_idx(vector<struct Agent> &vec, const unsigned int idx);

#endif /* ORACLE_HPP_ */
