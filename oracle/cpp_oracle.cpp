#include "cpp_oracle.hpp"

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

#include <utility>
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
#include <set>
#include <list>
#include <map>
#include <limits>
#include <algorithm>
#include <ilcplex/ilocplex.h>
#include <random>

ILOSTLBEGIN

// constants
constexpr array<float, 13> sn_l = {-0.2, 0.0, 0.6, -0.6, 0.4, -0.4, 0.2, 0.8, -0.14285714285714285, 0.3333333333333333, -0.8, 1.0, -1.0};
constexpr array<float, 13> sn_n = {45, 39, 23, 7, 18, 21, 42, 6, 1, 1, 5, 1, 1};
constexpr array<float, 13> tf_l = {-0.2, 0.0, 0.2, 0.6, 0.4, -0.6, 0.8, -0.4, -0.8, -0.5, -1.0, 1.0, -0.3333333333333333};
constexpr array<float, 13> tf_n = {31, 36, 31, 25, 21, 6, 18, 21, 11, 1, 3, 4, 2};
constexpr array<float, 11> ei_l = {-0.6, 1.0, 0.2, 0.6, -0.2, 0.8, 0.4, -1.0, -0.4, 0.0, -0.8};
constexpr array<float, 11> ei_n = {7, 43, 30, 45, 15, 24, 24, 3, 11, 7, 1};
constexpr array<float, 12> pj_l = {0.4, 0.2, 0.6, -0.2, 0.0, 0.8, -0.8, 0.6666666666666666, -0.4, 1.0, -0.6, 0.25};
constexpr array<float, 12> pj_n = {19, 53, 30, 39, 33, 10, 1, 1, 12, 5, 5, 2};
constexpr array<string_view, 7> competences = {"VERBAL", "LOGIC_MATHEMATICS", "VISUAL_SPATIAL", "KINESTESICA_CORPORAL", "MUSICAL_RHYTHMIC", "INTRAPERSONAL", "INTERPERSONAL"};
constexpr array<float, 18> verbal_l = {0.55, 0.7, 0.5, 0.65, 0.45, 0.6, 0.35, 0.25, 0.8, 0.85, 0.625, 0.75, 0.4, 0.95, 0.9, 0.3, 0.5416666666666666, 0.2};
constexpr array<float, 18> verbal_n = {29, 29, 21, 23, 20, 28, 7, 2, 11, 2, 1, 17, 7, 2, 5, 3, 2, 1};
constexpr array<float, 19> logic_mathematics_l = {0.5, 0.55, 0.65, 0.7, 0.8, 0.4, 0.45, 0.9, 0.15, 0.2, 0.25, 0.6, 0.3, 0.75, 0.35, 0.85, 0.95, 0.1, 0.6666666666666666};
constexpr array<float, 19> logic_mathematics_n = {19, 16, 26, 25, 11, 14, 11, 5, 2, 3, 4, 28, 5, 21, 8, 6, 4, 1, 1};
constexpr array<float, 15> visual_spatial_l = {0.45, 0.8, 0.55, 0.35, 0.6, 0.4583333333333333, 0.3, 0.5, 0.4, 0.25, 0.65, 0.2, 0.7, 0.75, 0.85};
constexpr array<float, 15> visual_spatial_n = {36, 7, 29, 30, 16, 1, 11, 27, 16, 7, 9, 4, 8, 6, 3};
constexpr array<float, 20> kinestesica_corporal_l = {0.55, 1.0, 0.6, 0.7, 0.65, 0.625, 0.5, 0.4, 0.2, 0.45, 0.75, 0.85, 0.8, 0.9, 0.15, 0.35, 0.25, 0.3, 0.95, 0.4583333333333333};
constexpr array<float, 20> kinestesica_corporal_n = {27, 2, 24, 23, 21, 1, 19, 10, 3, 17, 12, 9, 13, 6, 3, 4, 4, 6, 4, 2};
constexpr array<float, 21> musical_rhythmic_l = {0.65, 0.8, 0.3, 0.75, 0.85, 0.9166666666666666, 0.5, 0.25, 0.2, 0.9, 0.6666666666666666, 0.7, 0.55, 1.0, 0.35, 0.95, 0.6, 0.15, 0.45, 0.4, 0.1};
constexpr array<float, 21> musical_rhythmic_n = {16, 28, 7, 31, 15, 2, 10, 2, 1, 15, 1, 11, 10, 11, 10, 10, 9, 1, 7, 10, 3};
constexpr array<float, 18> intrapersonal_l = {0.7, 0.55, 0.35, 0.85, 0.75, 0.65, 0.6, 0.8, 0.5, 0.25, 0.45, 0.9, 0.95, 1.0, 0.4, 0.2, 0.5416666666666666, 0.7083333333333334};
constexpr array<float, 18> intrapersonal_n = {30, 24, 3, 11, 26, 31, 25, 14, 15, 1, 7, 10, 3, 4, 2, 1, 1, 2};
constexpr array<float, 23> interpersonal_l = {0.65, 0.95, 0.55, 0.8, 0.85, 0.7, 0.75, 0.9166666666666666, 0.05, 0.5, 0.25, 0.6, 0.875, 0.35, 0.9, 0.6875, 0.45, 0.625, 1.0, 0.4, 0.3, 0.9375, 0.5625};
constexpr array<float, 23> interpersonal_n = {21, 8, 9, 23, 16, 40, 24, 1, 1, 7, 1, 19, 2, 3, 11, 1, 7, 3, 2, 6, 2, 1, 2};

vector<struct Agent> cpp_sample_agents(size_t n, size_t seed) {

    // initialize PRNG
    random_device rd;
    mt19937 gen(rd());
    gen.seed(seed);

    // gender distribution (50% 50%)
    auto dist_gender = discrete_distribution<int>({1, 1});

    // personality distributions
    auto dist_sn = discrete_distribution<int>(sn_n.begin(), sn_n.end());
    auto dist_tf = discrete_distribution<int>(tf_n.begin(), tf_n.end());
    auto dist_ei = discrete_distribution<int>(ei_n.begin(), ei_n.end());
    auto dist_pj = discrete_distribution<int>(pj_n.begin(), pj_n.end());

    // competences distributions
    array<discrete_distribution<int>, 7> comp_dists = {
        discrete_distribution<int>(verbal_n.begin(), verbal_n.end()),
        discrete_distribution<int>(logic_mathematics_n.begin(), logic_mathematics_n.end()),
        discrete_distribution<int>(visual_spatial_n.begin(), visual_spatial_n.end()),
        discrete_distribution<int>(kinestesica_corporal_n.begin(), kinestesica_corporal_n.end()),
        discrete_distribution<int>(musical_rhythmic_n.begin(), musical_rhythmic_n.end()),
        discrete_distribution<int>(intrapersonal_n.begin(), intrapersonal_n.end()),
        discrete_distribution<int>(interpersonal_n.begin(), interpersonal_n.end())
    };

    // competences levels
    const array<vector<float>, 7> comp_levels = {
        vector<float>(verbal_l.begin(), verbal_l.end()),
        vector<float>(logic_mathematics_l.begin(), logic_mathematics_l.end()),
        vector<float>(visual_spatial_l.begin(), visual_spatial_l.end()),
        vector<float>(kinestesica_corporal_l.begin(), kinestesica_corporal_l.end()),
        vector<float>(musical_rhythmic_l.begin(), musical_rhythmic_l.end()),
        vector<float>(intrapersonal_l.begin(), intrapersonal_l.end()),
        vector<float>(interpersonal_l.begin(), interpersonal_l.end())
    };

    vector<struct Agent> agents(n);

    for (auto i = 0; i < n; ++i) {
        Agent ag;
        ag.id = i;
        ag.gender = dist_gender(gen);
        (ag.profile).sn = sn_l[dist_sn(gen)];
        (ag.profile).tf = tf_l[dist_tf(gen)];
        (ag.profile).ei = ei_l[dist_ei(gen)];
        (ag.profile).pj = pj_l[dist_pj(gen)];
        for (auto c = 0; c < competences.size(); ++c) {
            (ag.competence_level)[string(competences[c])] = comp_levels[c][comp_dists[c](gen)];
        }
        agents[i] = ag;
    }

    return agents;
}

vector<struct Agent> cpp_read_agents(const char *filename) {

    vector<struct Agent> agents;

    // read the complete set of students from the corresponding input file
    ifstream indata;
    indata.open(filename);
    if(!indata) { // file couldn't be opened
        cout << "Error: file containing all students could not be opened" << endl;
    }

    char c;
    while (indata >> c) {
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
        agents.push_back(ag);
    }
    indata.close();

    return agents;
}

pair<vector<string>,Task_type> cpp_read_task_competences(const char *filename) {

    vector<string> competences;
    unsigned int n_of_competences;
    Task_type task;

    // read the task information from the corresponding input file
    ifstream indata;
    indata.open(filename);
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

    return make_pair(competences, task);
}

// Parameter values. The value of alpha is set to beta/3.0 below. This is the always-used setting. If this changes some day, the code must be changed.
constexpr double alpha = 0.19;
constexpr double my_beta = alpha * 3.0;
constexpr double gender_gamma = 0.24;
constexpr double v = 0.5;

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *_team, const double lambda, const struct Data &data) {

    // convert input parameters
    set<int> team(_team, _team + actual_team_size);
    const vector<Agent> agents = data.agents;
    const vector<string> competences = data.competences;
    const unsigned int n_of_competences = competences.size();
    const Task_type task = data.task;
    //cout << "Read " << agents.size() << " students" << '\n';
    //cout << "Read " << n_of_competences << " competences" << '\n';

    // actual code
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
    ucon += gender_gamma * sin(M_PI * (double(n_of_women)/double(actual_team_size)));

    return (lambda*uprof + (1.0-lambda)*ucon);
}

void cpp_remove_idx(vector<struct Agent> &vec, const unsigned int idx) {

    vec.erase(vec.begin() + idx);
}
