#ifndef ORACLE_HPP_
#define ORACLE_HPP_

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team,
                 const unsigned int n_of_agents, const void *agents,
                 const unsigned int n_of_competences, const void *competences,
                 const void *task);

#endif /* ORACLE_HPP_ */
