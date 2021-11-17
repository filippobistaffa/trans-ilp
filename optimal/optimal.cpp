#include "optimal.hpp"

#include <sys/time.h>
#include <sstream>
#include <numeric>
#include <random>
#include <vector>
#include <string>
#include <queue>
#include <map>
#include <set>

// CPLEX
#include <ilcplex/ilocplex.h>

// Modules
#include "params.hpp"
#include "io.hpp"
#include "coal_type.hpp"
#include "log.hpp"

struct timeval t1, t2;

// Print variables
//#define PRINT_VARS

// Data Structures

struct Personality_profile {
    double sn, tf, ei, pj;
};

struct Agent {
    int id;
    int gender;
    Personality_profile profile;
    std::map<std::string, double> competence_level;
};

struct Competence {
    double level;
    double importance;
};

struct Task_type {
    std::map<std::string, Competence> required_competences;
};

std::vector<struct Agent> read_agents(const char *filename) {

    std::vector<struct Agent> agents;

    // read the complete set of students from the corresponding input file
    std::ifstream indata;
    indata.open(filename);
    if(!indata) { // file couldn't be opened
        std::cerr << "Error: file containing all students could not be opened\n";
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
            std::string comp;
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

std::pair<std::vector<std::string>, Task_type> read_task_competences(const char *filename) {

    std::vector<std::string> competences;
    int n_of_competences;
    Task_type task;

    // read the task information from the corresponding input file
    std::ifstream indata;
    indata.open(filename);
    if(!indata) { // file couldn't be opened
        std::cerr << "Error: file containing the task information could not be opened\n";
    }

    indata >> n_of_competences;
    double imp_sum = 0.0;
    for (int i = 0; i < n_of_competences; ++i) {
        Competence c;
        std::string comp_name;
        indata >> comp_name;
        indata >> c.level;
        indata >> c.importance;
        (task.required_competences)[comp_name] = c;
        imp_sum += c.importance;
        competences.push_back(comp_name);
    }
    indata.close();

    for (auto i = 0; i < n_of_competences; ++i) {
        (task.required_competences)[competences[i]].importance /= imp_sum;
    }

    return make_pair(competences, task);
}

// Parameter values. The value of alpha is set to beta/3.0 below. This is the always-used setting. If this changes some day, the code must be changed.
constexpr double alpha = 0.19;
constexpr double my_beta = alpha * 3.0;
constexpr double synteam_gamma = 0.24;
constexpr double v = 0.5;
constexpr double lambda = 0.8;

auto compute_value(coal c, const std::vector<Agent> &agents, const std::vector<std::string> &competences, const Task_type &task) {

    // convert input parameters
    const auto actual_team_size = c.c[0];
    std::set<int> team(c.c + 1, c.c + 1 + c.c[0]);
    const auto n_of_competences = competences.size();
    //cout << "Read " << agents.size() << " students" << '\n';
    //cout << "Read " << n_of_competences << " competences" << '\n';

    // actual code
    std::vector< std::vector<int> > assignment;
    std::vector< std::vector<double> > cost_matrix(actual_team_size, std::vector<double>(n_of_competences, 0.0));
    int ind = 0;
    int n_of_women = 0;
    for (std::set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
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

        assignment = std::vector< std::vector<int> >(actual_team_size, std::vector<int>(n_of_competences, 0));

        IloNumArray xan(env, actual_team_size*n_of_competences);
        cpl.getValues(xan, x);
        for (int i = 0; i < actual_team_size; ++i) {
            for (int j = 0; j < n_of_competences; ++j) {
                if (xan[(i*n_of_competences)+j] > 0.9) assignment[i][j] = 1;
            }
        }
    }
    catch (IloException& e) {
        std::cerr << "Concert exception caught: " << e << '\n';
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
        for (std::set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
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
    for (std::set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        sn_mean += (agents[*sit].profile).sn;
        tf_mean += (agents[*sit].profile).tf;
    }
    sn_mean = sn_mean/double(actual_team_size);
    tf_mean = tf_mean/double(actual_team_size);

    double sn_var = 0.0;
    double tf_var = 0.0;
    for (std::set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
        sn_var += ((agents[*sit].profile).sn - sn_mean)*((agents[*sit].profile).sn - sn_mean);
        tf_var += ((agents[*sit].profile).tf - tf_mean)*((agents[*sit].profile).tf - tf_mean);
    }
    sn_var = sqrt(sn_var/double(actual_team_size));
    tf_var = sqrt(tf_var/double(actual_team_size));

    double ucon = sn_var*tf_var;

    double alpha_max = 0.0;
    double my_beta_max = 0.0;
    for (std::set<int>::iterator sit = team.begin(); sit != team.end(); ++sit) {
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

template <typename cont, typename type>
__attribute__((always_inline)) inline
void print_var_array(cont vars, type &xa, IloCplex &cplex) {

    for (uint i = 0; i < xa.getSize(); i++) {
        try {
            if (fabs(cplex.getValue(xa[i])) > EPSILON)
                std::cout << xa[i].getName() << " = " << vars[i].w << '\n';
        }
        catch (IloException& e) { e.end(); }
    }
    puts("");
}

auto generate_vars(const std::vector<Agent> &agents, const std::vector<std::string> &competences, const Task_type &task) {

    const auto n = agents.size();
    std::deque<coal> vars;
    std::vector<bool> select(n);
    std::fill(select.end() - K, select.end(), true);

    do {
        coal c = {
            {5},
            0
        };
        auto k = 1;
        for (auto i = 0; i < n; ++i) {
            if (select[i]) {
                c.c[k++] = i;
            }
        }
        c.w = compute_value(c, agents, competences, task);
        vars.push_back(c);
    } while (std::next_permutation(select.begin(), select.end()));

    return vars;
}

inline bool exists(const char *filename) {

    FILE *file = fopen(filename, "r");
    if (!file) {
        return false;
    } else {
        fclose(file);
        return true;
    }
}

int main(int argc, char *argv[]) {

    char *instance_file = nullptr;
    char *task_file = nullptr;
    int opt;

    while ((opt = getopt(argc, argv, "i:t:")) != -1) {
        switch (opt) {
            case 'i':
                if (exists(optarg)) {
                    instance_file = optarg;
                } else {
                    std::cerr << argv[0] << ": file not found -- '";
                    std::cerr << optarg << "'" << '\n';
                    return EXIT_FAILURE;
                }
                continue;
            case 't':
                if (exists(optarg)) {
                    task_file = optarg;
                } else {
                    std::cerr << argv[0] << ": file not found -- '";
                    std::cerr << optarg << "'" << '\n';
                    return EXIT_FAILURE;
                }
                continue;
            default:
                return EXIT_FAILURE;
        }
    }

    if (!instance_file) {
        std::cerr << argv[0] << ": instance not specified!" << '\n';
        return EXIT_FAILURE;
    }

    if (!task_file) {
        std::cerr << argv[0] << ": task not specified!" << '\n';
        return EXIT_FAILURE;
    }

    log_line();
    log_value("Instance", instance_file, "i");
    log_value("Task", task_file, "t");
    log_line();
    log_value("Alpha", alpha);
    log_value("Beta", my_beta);
    log_value("Gamma", gamma);
    log_value("Lambda", lambda);
    log_line();

    auto agents = read_agents(instance_file);
    auto [ competences, task ] = read_task_competences(task_file);
    const auto n = agents.size();

    // BEGIN GENERATION

    std::cout << "\nGenerating decision variables...\n";
    gettimeofday(&t1, nullptr);
    auto vars = generate_vars(agents, competences, task);

    #ifdef PRINT_VARS
    std::cout << "Variables:\n";
    print_coals(vars);
    std::cout << '\n';
    #endif

    IloEnv env;
    IloIntVarArray xa(env);
    IloModel model(env);
    IloExprArray constr(env, n);
    IloExpr obj(env);

    // Initialise empty constraints (avoids segfaults)
    for (auto i = 0; i < n; ++i) {
        constr[i] = IloExpr(env);
    }

    for (auto it = vars.begin() ; it != vars.end(); ++it) {

        // Create variable
        std::ostringstream ostr;
        ostr << "X_[" << it->c[1];
        for (uint i = 1; i < it->c[0]; ++i)
            ostr << "," << it->c[i + 1];
        ostr << "]";
        //cout << ostr.str() << '\n';
        IloIntVar x = IloIntVar(env, 0, 1, ostr.str().c_str());
        xa.add(x);

        // Update constraints
        for (auto i = 0; i < it->c[0]; ++i) {
            constr[it->c[i + 1]] += x;
        }

        // Update objective function
        obj += log(it->w) * x;
    }

    model.add(IloMaximize(env, obj));
    obj.end();

    // Finalise creation of constraints for Weighted Set Packing
    for (auto i = 0; i < n; ++i) {
        model.add(constr[i] == 1);
        constr[i].end();
    }

    gettimeofday(&t2, nullptr);
    const double gen_time = (double)(t2.tv_usec - t1.tv_usec) / 1e6 + t2.tv_sec - t1.tv_sec;

    IloCplex cplex(model);
    cplex.setParam(IloCplex::Threads, 1);
    cplex.setParam(IloCplex::MIPDisplay, 4);

    // END GENERATION / BEGIN SOLUTION

    #ifdef HIDE_CPLEX
    cplex.setOut(env.getNullStream());
    #endif

    gettimeofday(&t1, nullptr);

    try {
        if (!cplex.solve()) {
            env.out() << "Unable to find a solution" << '\n';
            exit(EXIT_FAILURE);
        }
    }
    catch (IloCplex::Exception e) {
        env.out() << "An exception occurred" << '\n';
        exit(EXIT_FAILURE);
    }

    gettimeofday(&t2, nullptr);
    const double sol_time = (double)(t2.tv_usec - t1.tv_usec) / 1e6 + t2.tv_sec - t1.tv_sec;

    // END SOLUTION

    std::cout << "\nOptimal solution:\n";
    print_var_array(vars, xa, cplex);

    log_line();
    log_value("Optimal value", exp(cplex.getObjValue()));
    log_value("Generation runtime", gen_time);
    log_value("Solution runtime", sol_time);
    log_value("Total runtime", gen_time + sol_time);
    log_line();

    return EXIT_SUCCESS;
}
