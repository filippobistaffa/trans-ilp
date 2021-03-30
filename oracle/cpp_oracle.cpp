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

ILOSTLBEGIN

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

    // write results to output parameter
    return make_pair(competences, task);
}

// Parameter values. The value of alpha is set to beta/3.0 below. This is the always-used setting. If this changes some day, the code must be changed.
constexpr double alpha = 0.19;
constexpr double my_beta = alpha * 3.0;
constexpr double synteam_gamma = 0.24;
constexpr double v = 0.5;
constexpr double lambda = 0.8;

float cpp_oracle(const unsigned int actual_team_size, const unsigned int *_team, const struct Data data) {

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
    ucon += synteam_gamma*sin(M_PI * (double(n_of_women)/double(actual_team_size)));

    return (lambda*uprof + (1.0-lambda)*ucon); 
}
