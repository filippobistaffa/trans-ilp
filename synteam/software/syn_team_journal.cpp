/***************************************************************************
                      syn_team_journal.cpp  -  description
                             -------------------
    begin                : Wed Nov 7 2018
    copyright            : (C) 2018 by Christian Blum
    email                : christian.blum@iiia.csic.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "Timer.h"
#include <vector>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string.h>
#include <fstream>
#include <sstream>
#include <cmath>
#include <math.h>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <vector>
#include <set>
#include <list>
#include <map>
#include <limits>
#include <algorithm>
#include <ilcplex/ilocplex.h>

ILOSTLBEGIN

// Data Structures

struct Personality_profile {
    double sn, tf, ei, pj;
};

struct Agent {
    int id;
    int gender;
    Personality_profile profile;
    map<string,double> competence_level;
};

struct Competence {
    double level;
    double importance;
};

struct Task_type {
    map<string,Competence> required_competences;
};

struct Team {
    set<int> agents;
    double syn_val;
};

struct Solution {
    vector<Team> teams;
    double value;
};

// Data structures for the problem data
vector<string> competences;
vector<Agent> all_agents;
vector<Agent> agents;
Task_type task;
int n_of_agents;
int total_n_of_agents;
int n_of_competences;
int wanted_team_size;
vector<int> team_size;

// Parameter values. The value of alpha is set to beta/3.0 below. This is the always-used setting. If this changes some day, the code must be changed.
double alpha = 0.19;
double my_beta;
double synteam_gamma = 0.24;
double v = 0.5;
double lambda = 0.8;

// variables for reading the input information from files
string all_students_file;
string task_file;
int n_of_subsets;

inline int stoi(string &s) {

  return atoi(s.c_str());
}

inline double stof(string &s) {

  return atof(s.c_str());
}

void read_parameters(int argc, char **argv) {

    int iarg = 1;

    while (iarg < argc) {
        if (strcmp(argv[iarg],"-i_all_stud")==0) all_students_file = argv[++iarg];
        else if (strcmp(argv[iarg],"-i_task")==0) task_file = argv[++iarg];
        else if (strcmp(argv[iarg],"-n_agents")==0) n_of_agents = atoi(argv[++iarg]);
        else if (strcmp(argv[iarg],"-teamsize")==0) wanted_team_size = atoi(argv[++iarg]);
        else if (strcmp(argv[iarg],"-n_subsets")==0) n_of_subsets = atoi(argv[++iarg]);
        else if (strcmp(argv[iarg],"-lambda")==0) lambda = atof(argv[++iarg]);
        else if (strcmp(argv[iarg],"-alpha")==0) alpha = atof(argv[++iarg]);
        else if (strcmp(argv[iarg],"-gamma")==0) synteam_gamma = atof(argv[++iarg]);
        else if (strcmp(argv[iarg],"-v")==0) v = atof(argv[++iarg]);
        iarg++;
    }
}

double compute_synergistic_value(set<int>& team) {

    int actual_team_size = int(team.size());
    vector< vector<int> > assignment;
    vector< vector<double> > cost_matrix(actual_team_size, vector<double>(n_of_competences, 0.0));
    int ind = 0;
    int n_of_women = 0;
    for (set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        if (agents[*sit].gender == 1) ++n_of_women;
        for (int j = 0; j < n_of_competences; ++j) {
            double tcost;
            double diff = (agents[*sit].competence_level)[competences[j]] - ((task.required_competences)[competences[j]]).level;
            if (diff < 0.0) {
                diff *= -1.0;
                tcost = diff*v*((task.required_competences)[competences[j]]).importance;
            }
            else tcost = diff*(1.0-v)*((task.required_competences)[competences[j]]).importance;
            cost_matrix[ind][j] = tcost;
        }
        ++ind;
    }

    IloEnv env;
    env.setOut(env.getNullStream());
    try{
        IloModel model(env);

        IloNumVarArray x(env, actual_team_size*n_of_competences, 0, 1, ILOINT);

        IloExpr obj(env);
        for (int i = 0; i < actual_team_size; ++i) {
            for (int j = 0; j < n_of_competences; ++j) obj += x[(i*n_of_competences)+j]*cost_matrix[i][j];
        }
        model.add(IloMinimize(env, obj));
        obj.end();

        int tcap = n_of_competences/actual_team_size;
        if (not(n_of_competences%actual_team_size == 0)) ++tcap;
        for (int i = 0; i < actual_team_size; ++i) {
            IloNumExpr expr(env);
            for (int j = 0; j < n_of_competences; ++j) expr += x[(i*n_of_competences)+j];
            model.add(expr <= tcap);
            expr.end();
            if (n_of_competences >= actual_team_size) {
                IloNumExpr expr3(env);
                for (int j = 0; j < n_of_competences; ++j) expr3 += x[(i*n_of_competences)+j];
                model.add(expr3 >= 1);
                expr3.end();
            }
        }

        for (int j = 0; j < n_of_competences; ++j) {
            IloNumExpr expr(env);
            for (int i = 0; i < actual_team_size; ++i) expr += x[(i*n_of_competences)+j];
            model.add(expr == 1);
            expr.end();
        }

        IloCplex cpl(model);
        cpl.setParam(IloCplex::Threads, 1);

        cpl.solve();

        assignment = vector< vector<int> >(actual_team_size, vector<int>(n_of_competences, 0));

        IloNumArray xan(env, actual_team_size*n_of_competences);
        cpl.getValues(xan, x);
        for (int i = 0; i < actual_team_size; ++i) {
            for (int j = 0; j < n_of_competences; ++j) {
                if (xan[(i*n_of_competences)+j] > 0.9) assignment[i][j] = 1;
            }
        }
    }
    catch (IloException& e) {
        cerr << "Concert exception caught: " << e << endl;
    }
    env.end();

    double uprof;
    double u = 0.0;
    double o = 0.0;
    for (int j = 0; j < n_of_competences; ++j) {
        double usum = 0.0;
        double osum = 0.0;
        int ucnt = 0;
        int ocnt = 0;
        int i = 0;
        for (set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
            if (assignment[i][j] == 1) {
                double diff = (agents[*sit].competence_level)[competences[j]] - ((task.required_competences)[competences[j]]).level;
                if (diff < 0.0) {
                    ++ucnt;
                    usum += -1.0*diff;
                }
                else if (diff > 0.0) {
                    ++ocnt;
                    osum += diff;
                }
            }
            ++i;
        }
        u += ((task.required_competences)[competences[j]]).importance * (usum/double(ucnt + 1));
        o += ((task.required_competences)[competences[j]]).importance * (osum/double(ocnt + 1));
    }
    uprof = 1.0 - (v*u + (1.0 - v)*o);

    double sn_mean = 0.0;
    double tf_mean = 0.0;
    for (set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        sn_mean += (agents[*sit].profile).sn;
        tf_mean += (agents[*sit].profile).tf;
    }
    sn_mean = sn_mean/double(actual_team_size);
    tf_mean = tf_mean/double(actual_team_size);

    double sn_var = 0.0;
    double tf_var = 0.0;
    for (set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        sn_var += ((agents[*sit].profile).sn - sn_mean)*((agents[*sit].profile).sn - sn_mean);
        tf_var += ((agents[*sit].profile).tf - tf_mean)*((agents[*sit].profile).tf - tf_mean);
    }
    sn_var = sqrt(sn_var/double(actual_team_size));
    tf_var = sqrt(tf_var/double(actual_team_size));

    double ucon = sn_var*tf_var;

    double alpha_max = 0.0;
    double my_beta_max = 0.0;
    for (set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        if ((agents[*sit].profile).tf > 0.0 and (agents[*sit].profile).ei > 0.0 and (agents[*sit].profile).pj > 0.0) {
            double vec_prod = alpha*(agents[*sit].profile).tf + alpha*(agents[*sit].profile).ei + alpha*(agents[*sit].profile).pj;
            if (vec_prod > alpha_max) alpha_max = vec_prod;
        }
        double bprod = -1.0*my_beta*(agents[*sit].profile).ei;
        if (bprod > my_beta_max) my_beta_max = bprod;
    }
    ucon += alpha_max + my_beta_max;
    ucon += synteam_gamma*sin(M_PI * (double(n_of_women)/double(actual_team_size)));

    return (lambda*uprof + (1.0-lambda)*ucon); 
}

void check_swap(Solution& sol, int tc1, int tc2, int ag1, int ag2, set<int>& team1, set<int>& team2, double& val1, double& val2, map<long, double>& team_value, int& poss) {

    team1 = (sol.teams)[tc1].agents;
    team2 = (sol.teams)[tc2].agents;
    team1.erase(ag1);
    team2.insert(ag1);
    team2.erase(ag2);
    team1.insert(ag2);

    stringstream ss_int;
    ss_int << "1";
    for(set<int>::iterator sit = team1.begin(); sit != team1.end(); ++sit) ss_int << std::setw(poss) << std::setfill('0') << *sit;
    long key = std::stol(ss_int.str());
    if (team_value.count(key) == 0) {
        val1 = compute_synergistic_value(team1);
        team_value[key] = val1;
    }
    else val1 = team_value[key];

    ss_int.str(std::string());
    ss_int << "1";
    for(set<int>::iterator sit = team2.begin(); sit != team2.end(); ++sit) ss_int << std::setw(poss) << std::setfill('0') << *sit;
    key = std::stol(ss_int.str());
    if (team_value.count(key) == 0) {
        val2 = compute_synergistic_value(team2);
        team_value[key] = val2;
    }
    else val2 = team_value[key];
}

void find_best_team_partition(set<int>& team1, set<int>& team2, double& val1, double& val2, map<long, double>& team_value, int& poss) {

    vector<int> agent_list;
    for (set<int>::iterator sit = team1.begin(); sit != team1.end(); ++sit) agent_list.push_back(*sit);
    for (set<int>::iterator sit = team2.begin(); sit != team2.end(); ++sit) agent_list.push_back(*sit);
    int K = team1.size();
    int N = K;
    N += team2.size();

    string bitmask(K, 1); // K leading 1's
    bitmask.resize(N, 0); // N-K trailing 0's

    bool started = false;
    do {
        if (not started) started = true;
        else {
            stringstream ss_int1, ss_int2;
            ss_int1 << "1";
            ss_int2 << "1";
            set<int> test_team1;
            set<int> test_team2;
            for (int i = 0; i < int(agent_list.size()); ++i) {
                if (bitmask[i]) {
                    test_team1.insert(agent_list[i]);
                    ss_int1 << std::setw(poss) << std::setfill('0') << agent_list[i];
                }
                else {
                    test_team2.insert(agent_list[i]);
                    ss_int2 << std::setw(poss) << std::setfill('0') << agent_list[i];
                }
            }
            long key1 = std::stol(ss_int1.str());
            long key2 = std::stol(ss_int2.str());
            double syn_val1;
            if (team_value.count(key1) == 0) {
                syn_val1 = compute_synergistic_value(test_team1);
                team_value[key1] = syn_val1;
            }
            else syn_val1 = team_value[key1];
            double syn_val2;
            if (team_value.count(key2) == 0) {
                syn_val2 = compute_synergistic_value(test_team2);
                team_value[key2] = syn_val2;
            }
            else syn_val2 = team_value[key2];
            if (syn_val1*syn_val2 > val1*val2) {
                val1 = syn_val1;
                val2 = syn_val2;
                team1 = test_team1;
                team2 = test_team2;
            }
        }
    } while (std::prev_permutation(bitmask.begin(), bitmask.end()));
}

void generate_solution(Solution& sol, set<int>& all_agent_indices, map<long, double>& team_value, int& poss) {

    sol.value = 1.0;
    set<int> agent_indices = all_agent_indices;
    int ind = 0;
    while (int(agent_indices.size()) > 0) {
        stringstream ss_int;
        ss_int << "1";
        set<int> rand_team;
        if (int(agent_indices.size()) == team_size[ind]) {
            rand_team = agent_indices;
            agent_indices.clear();
        }
        else {
            for (int k = 0; k < team_size[ind]; ++k) {
                int rnd = rand() % int(agent_indices.size());
                set<int>::iterator sit = agent_indices.begin();
                advance(sit, rnd);
                rand_team.insert(*sit);
                agent_indices.erase(*sit);
            }
        }
        for (set<int>::iterator ssit = rand_team.begin(); ssit != rand_team.end(); ++ssit) {
            ss_int << std::setw(poss) << std::setfill('0') << *ssit;
        }
        long key = std::stol(ss_int.str());
        Team new_team;
        new_team.agents = rand_team;
        if (team_value.count(key) == 0) {
            new_team.syn_val = compute_synergistic_value(rand_team);
            team_value[key] = new_team.syn_val;
        }
        else new_team.syn_val = team_value[key];
        sol.value *= new_team.syn_val;
        (sol.teams).push_back(new_team);
        ++ind;
    }
}

void check_solution(Solution& sol) {

    int n_of_teams = int((sol.teams).size());
    int n_of_ag = 0;
    for (int tc1 = 0; tc1 < n_of_teams; ++tc1) n_of_ag += int(((sol.teams)[tc1].agents).size());
    if (n_of_ag != n_of_agents) cout << "teams have not the correct number of agents" << endl;
    vector<bool> agent_used(n_of_agents, false);
    for (int tc1 = 0; tc1 < n_of_teams; ++tc1) {
        for (set<int>::iterator sit1 = ((sol.teams)[tc1].agents).begin(); sit1 != ((sol.teams)[tc1].agents).end(); ++sit1) {
            if (agent_used[*sit1]) cout << "OHOH, found an already used agent in a team." << endl;
            else agent_used[*sit1] = true;
        }
    }
    for (int i = 0; i < n_of_agents; ++i) {
        if (not agent_used[i]) cout << "OHOH, exists an unused agent" << endl;
    }
}

/**********
Main function
**********/

int main( int argc, char **argv ) {

    srand (time(NULL));

    read_parameters(argc,argv);
    
    std::cout << std::setprecision(11) << std::fixed;

    vector<double> times(n_of_subsets, 0.0);
    vector<double> total_times(n_of_subsets, 0.0);
    vector<double> results(n_of_subsets, 0.0);

    // read the complete set of students from the corresponding input file
    ifstream indata;
    indata.open(all_students_file.c_str());
    if(!indata) { // file couldn't be opened
        cout << "Error: file containing all students could not be opened" << endl;
    }

    total_n_of_agents = 0;
    char c;
    while (indata >> c) {
        ++total_n_of_agents;
        Agent ag;
        indata >> ag.id;
        indata >> c;
        indata >> c;
        indata >> c;
        while (c != '"') indata >> c;
        indata >> c;
        indata >> ag.gender;
        indata >> c;
        indata >> (ag.profile).sn;
        indata >> c;
        indata >> (ag.profile).tf;
        indata >> c;
        indata >> (ag.profile).ei;
        indata >> c;
        indata >> (ag.profile).pj;
        indata >> c;
        indata >> c;
        while (c != ']') {
            indata >> c;
            indata >> c;
            indata >> c;
            string comp;
            while (c != '"') {
                comp.push_back(c);
                indata >> c;
            }
            indata >> c;
            double level;
            indata >> level;
            (ag.competence_level)[comp] = level;
            indata >> c;
            indata >> c;
        }
        indata >> c;
        indata >> c;
        all_agents.push_back(ag);
    }
    indata.close();

    // read the task information from the corresponding input file
    indata.open(task_file.c_str());
    if(!indata) { // file couldn't be opened
        cout << "Error: file containing the task information could not be opened" << endl;
    }

    indata >> n_of_competences;
    double imp_sum = 0.0;
    for (int i = 0; i < n_of_competences; ++i) {
        Competence c;
        string comp_name;
        indata >> comp_name;
        indata >> c.level;
        indata >> c.importance;
        (task.required_competences)[comp_name] = c;
        imp_sum += c.importance;
        competences.push_back(comp_name);
    }
    indata.close();
    for (int i = 0; i < n_of_competences; ++i) (task.required_competences)[competences[i]].importance /= imp_sum;

    // fixed setting for beta (CAUTION!!!)
    my_beta = alpha*3.0;

    for (int iter = 0; iter < n_of_subsets; ++iter) {

        // read the subset of students to be considered from the corresponding input file
        stringstream ss;
        ss << "./instances_journal_final/subset_size_" << n_of_agents << "_wanted_team_size_" << wanted_team_size << "." << iter+1;
        string subset_students_file = ss.str();
        indata.open(subset_students_file.c_str());
        if(!indata) { // file couldn't be opened
            cout << "Error: file containing the subset of students to be considered could not be opened" << endl;
        }

        agents.clear();
        int agent_id;
        while (indata >> agent_id) agents.push_back(all_agents[agent_id]);
        indata.close();

        //determine the sizes of the different teams
        map<int,int> teams;
        int b = n_of_agents/wanted_team_size;
        set<int> team_size_multiples;
        if (n_of_agents >= wanted_team_size and n_of_agents%wanted_team_size == 0) {
            teams[b] = wanted_team_size;
            team_size_multiples.insert(b);
        }
        else if (n_of_agents >= wanted_team_size and n_of_agents%wanted_team_size <= b) {
            teams[n_of_agents%wanted_team_size] = wanted_team_size + 1;
            teams[b - (n_of_agents%wanted_team_size)] = wanted_team_size;
            team_size_multiples.insert(n_of_agents%wanted_team_size);
            team_size_multiples.insert(b - (n_of_agents%wanted_team_size));
        }
        else {
            teams[b] = wanted_team_size;
            teams[1] = n_of_agents%wanted_team_size;
            team_size_multiples.insert(b);
            team_size_multiples.insert(1);
        }
        int n_of_teams = 0;
        for (set<int>::iterator sit = team_size_multiples.begin(); sit != team_size_multiples.end(); ++sit) n_of_teams += *sit;
        int max_team_size = 0;
        team_size = vector<int>(n_of_teams, 0);
        int ind = 0;
        for (set<int>::reverse_iterator sit = team_size_multiples.rbegin(); sit != team_size_multiples.rend(); ++sit) {            
            for (int l = 0; l < *sit; ++l) {
                //cout << " " << teams[*sit];
                team_size[ind] = teams[*sit];
                if (teams[*sit] > max_team_size) max_team_size = teams[*sit];
                ++ind;
            }
        }
        //cout << endl;

        set<int> all_agent_indices;
        for (int j = 0; j < n_of_agents; ++j) all_agent_indices.insert(j);

        // the computation time starts now
        Timer timer;

        cout << "start run " << iter + 1 << endl;

        int poss = 0;
        int noa = n_of_agents;
        while (noa > 0) {
            noa /= 10;
            ++poss;
        }
        map<long, double> team_value;

        double best_sol_val = 0.0;

        double ctime;

        Solution sol;
        generate_solution(sol, all_agent_indices, team_value, poss);
        if (sol.value > best_sol_val) {
            double ctime = timer.elapsed_time(Timer::VIRTUAL);
            cout << "value " << sol.value << "\ttime " << ctime << endl;
            results[iter] = sol.value;
            times[iter] = ctime;
            best_sol_val = sol.value;
        }
        //check_solution(sol);

        int n_r = int(1.5*double(n_of_teams));
        int n_l = int(double(n_r)/6.0);
        int c_r = 1;
        int c_l = 1;
        while (c_r <= n_r) {
            int t1 = rand() % n_of_teams;
            int t2 = t1;
            while (t2 == t1) t2 = rand() % n_of_teams;
            set<int> team1 = (sol.teams)[t1].agents;
            set<int> team2 = (sol.teams)[t2].agents;
            double val1 = (sol.teams)[t1].syn_val;
            double val2 = (sol.teams)[t2].syn_val;
            find_best_team_partition(team1, team2, val1, val2, team_value, poss);
            bool impr_found = true;
            if (val1*val2 <= (sol.teams)[t1].syn_val*(sol.teams)[t2].syn_val and c_l == n_l) {
                impr_found = false;
                for (int tc1 = 0; tc1 < n_of_teams and (not impr_found); ++tc1) {
                    for (set<int>::iterator sit1 = ((sol.teams)[tc1].agents).begin(); sit1 != ((sol.teams)[tc1].agents).end() and (not impr_found); ++sit1) {
                        for (int tc2 = tc1 + 1; tc2 < n_of_teams and (not impr_found); ++tc2) {
                            for (set<int>::iterator sit2 = ((sol.teams)[tc2].agents).begin(); sit2 != ((sol.teams)[tc2].agents).end() and (not impr_found); ++sit2) {
                                 check_swap(sol, tc1, tc2, *sit1, *sit2, team1, team2, val1, val2, team_value, poss);
                                 if (val1*val2 > (sol.teams)[tc1].syn_val*(sol.teams)[tc2].syn_val) {
                                     impr_found = true;
                                     t1 = tc1;
                                     t2 = tc2;
                                 }
                            }
                        }
                    }
                }
            }
            if (val1*val2 > (sol.teams)[t1].syn_val*(sol.teams)[t2].syn_val and impr_found) {
                c_r = 1;
                c_l = 1;
                sol.value /= (sol.teams)[t1].syn_val;
                sol.value /= (sol.teams)[t2].syn_val;
                sol.value *= (val1*val2);
                if (sol.value > best_sol_val) {
                    double ctime = timer.elapsed_time(Timer::VIRTUAL);
                    cout << "value " << sol.value << "\ttime " << ctime << endl;
                    results[iter] = sol.value;
                    times[iter] = ctime;
                    best_sol_val = sol.value;
                }
                (sol.teams)[t1].agents = team1;
                (sol.teams)[t1].syn_val = val1;
                (sol.teams)[t2].agents = team2;
                (sol.teams)[t2].syn_val = val2;
                /*
                if (just_checked) {
                    cout << "just checked" << endl;
                    cout << t1 << "\t" << t2 << endl;
                }
                else cout << "NOT just checked" << endl;
                check_solution(sol);
                */
            }
            else {
                c_r += 1;
                c_l += 1;
            }
        }
        ctime = timer.elapsed_time(Timer::VIRTUAL);
        cout << "total_time: " << ctime << endl;
        total_times[iter] = ctime;
        cout << "end run " << iter + 1 << endl;
        team_value.clear();
    }
    double r_mean = 0.0;
    double t_mean = 0.0;
    double tt_mean = 0.0;
    for (int i = 0; i < results.size(); i++) {
        r_mean = r_mean + results[i];
        t_mean = t_mean + times[i];
        tt_mean = tt_mean + total_times[i];
    }
    r_mean = r_mean / ((double)results.size());
    t_mean = t_mean / ((double)times.size());
    tt_mean = tt_mean / ((double)total_times.size());
    double rsd = 0.0;
    double tsd = 0.0;
    double ttsd = 0.0;
    for (int i = 0; i < results.size(); i++) {
        rsd = rsd + pow(results[i]-r_mean,2.0);
        tsd = tsd + pow(times[i]-t_mean,2.0);
        ttsd = ttsd + pow(total_times[i]-tt_mean,2.0);
    }
    rsd = rsd / ((double)(results.size()-1.0));
    if (rsd > 0.0) {
        rsd = sqrt(rsd);
    }
    tsd = tsd / ((double)(times.size()-1.0));
    if (tsd > 0.0) {
        tsd = sqrt(tsd);
    }
    ttsd = ttsd / ((double)(total_times.size()-1.0));
    if (ttsd > 0.0) {
        ttsd = sqrt(ttsd);
    }
    cout << r_mean << "\t" << rsd << "\t" << t_mean << "\t" << tsd << "\t" << tt_mean << "\t" << ttsd << endl;
}

