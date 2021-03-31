#include "ilp.hpp"

auto read_vars(const char *filename) {

    std::vector<coal> vars;
	std::ifstream f(filename);
	std::string str;
	auto n = 0;

	while (getline(f, str)) {
		char *dup = strdup(str.c_str());
		char *token = strtok(dup, ",");
		coal c;
		c.w = atof(token);
		token = strtok(NULL, ",");
		c.c[0] = 0;
		while (token != NULL) {
            auto a = std::stoi(token);
			c.c[++c.c[0]] = a;
			n = std::max(a, n);
			token = strtok(NULL, ",");
		}
		vars.push_back(c);
		free(dup);
	}

	f.close();
    return make_pair(vars, n + 1);
}

template <typename cont, typename type>
void print_solution(cont &vars, type &xa, IloCplex &cplex) { //, const std::std::vector<req> &reqs, const std::std::vector<value> &time) {

	for (auto i = 0; i < xa.getSize(); ++i) {
		try {
			if (fabs(cplex.getValue(xa[i])) > EPSILON) {
				std::cout << xa[i].getName() << '\n';
				//coal c = *std::next(vars.begin(), i);
				//print_buf(c.p, 2 * c.c[0], "Path");
				//printf("Distance reduction = %.2f\n", c.dr);
				//print_buf(c.qos.icd, c.c[0], "In-car delays");
				//print_buf(c.qos.qos, c.c[0], "QoS values", "%.2f");
			}
		}
		catch (IloException& e) { e.end(); }
	}
	puts("");
}

int main(int argc, char *argv[]) {

	if (argc != 3) {
		printf(RED("Usage: %s VARS_CSV TIME_BUDGET\n"), argv[0]);
		return EXIT_FAILURE;
	}

	// Parse commandline arguments
	auto i = 1;
	auto [ vars, n ] = read_vars(argv[i++]);
	const float tb = atof(argv[i++]); // Seconds

	#ifdef PRINT_VARS
	std::cout << CYAN("Variables:") << '\n';
	print_coals(vars.begin(), vars.end());
	std::cout << '\n';
	#endif

	// CPLEX data structures
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
		//ostr << "X_[" << reqs[it->c[1]];
		ostr << it->c[1];
		for (auto i = 1; i < it->c[0]; ++i) {
			ostr << "," << it->c[i + 1];
		}
		//ostr << "]";
		//std::cout << ostr.str() << '\n';
		IloIntVar x = IloIntVar(env, 0, 1, ostr.str().c_str());
		xa.add(x);
		// Update constraints
		for (auto i = 0; i < it->c[0]; ++i) {
			constr[it->c[i + 1]] += x;
		}
		// Update objective function
		obj += it->w * x;
	}

	//std::cout << '\n' << "Objective function:" << '\n' << obj << '\n';
	model.add(IloMaximize(env, obj));
	obj.end();

	// Finalise creation of constraints for Weighted Set Packing
	for (auto i = 0; i < n; ++i) {
		model.add(constr[i] <= 1);
		constr[i].end();
	}

	IloCplex cplex(model);
	#if CPX_VERSION >= 12060000
	cplex.setParam(IloCplex::Param::TimeLimit, tb);
	#else
	cplex.setParam(IloCplex::TiLim, tb);
	#endif
	//cplex.setParam(IloCplex::Threads, n_threads);
	cplex.setParam(IloCplex::MIPDisplay, 4);

	#ifdef EXPORT_ILP
	char lp_name[50];
	strcpy(lp_name, argv[1]);
	strcat(lp_name, ".lp");
	std::cout << "ILP model exported to " << lp_name << '\n';
	cplex.exportModel(lp_name);
	#endif

	#ifdef HIDE_CPLEX
	cplex.setOut(env.getNullStream());
	std::cout << BLUE("Solving ILP model...") << '\n';
	#else
	std::cout << BLUE("Solving ILP model:") << '\n';
	#endif

	try {
		if (!cplex.solve()) {
			std::cout << RED("Unable to find a solution") << '\n';
			exit(EXIT_FAILURE);
		}
	}
	catch (IloCplex::Exception e) {
		std::cout << RED("An exception occurred") << '\n';
		exit(EXIT_FAILURE);
	}

	// End solution

	std::cout << '\n';
	#ifdef PRINT_SOLUTION
	std::cout << GREEN("Solution:") << '\n';
	print_solution(vars[0], xa, cplex);
	#endif
	std::cout << cplex.getObjValue() << '\n';

	return EXIT_SUCCESS;
}
