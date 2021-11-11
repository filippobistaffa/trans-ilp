#include "pg2.hpp"

template <typename type1, typename type2>
__attribute__((always_inline)) inline
type1 if_not_zero(type1 x, type2 y) {

    return x ? x : y;
}

int main(int argc, char *argv[]) {

    if (argc != 10 && argc != 11) {
        printf(RED("Usage: %s REQUEST_SEQUENCE DISTANCE_MATRIX TIME_MATRIX SEED GENERATION_TIME_BUDGET DETERMINISM_RATE CANDIDATE_LIST_LENGTH #THREADS ENV_BENEFIT_K\n"), argv[0]);
        return EXIT_FAILURE;
    }

    // Data structures
    vector<req> reqs;
    vector<step> steps;
    vector<step> deltas;
    vector<value> distance;
    vector<value> time;

    // Parse commandline arguments
    auto i = 1;
    read_reqs(argv[i++], reqs, steps, deltas);
    const req n = reqs.size();
    read_matrix(argv[i++], Z, Z, distance);
    read_matrix(argv[i++], Z, Z, time);
    const uint seed = atoi(argv[i++]);
    const float gtb = atof(argv[i++]) * 1e3; // Milliseconds
    const float dr = atof(argv[i++]);
    const uint cl = if_not_zero(atoi(argv[i++]), UINT_MAX);
    const uint n_threads = if_not_zero(atoi(argv[i++]), omp_get_max_threads());
    const float env_k = atof(argv[i++]);

    #ifdef PRINT_INPUT
    cout << CYAN("Input:") << endl;
    print_it(reqs.begin(), reqs.end(), "reqs");
    print_it(steps.begin(), steps.end(), "steps");
    print_mat(distance.begin(), distance.end(), Z, "distance", "% 6.0f");
    print_mat(time.begin(), time.end(), Z, "time", "% 5.0f");
    //print_vec(deltas, "deltas");
    //print_vec(costs, "costs");
    cout << "Environmental benefit weight = " << env_k << endl;
    cout << endl;
    #endif

    // Probabilistic behaviour
    random_device rd;
    uniform_real_distribution<> ur(0.0, 1.0);
    uniform_int_distribution<> ui(0, cl - 1);

    // Begin ILP generation

    vector<vector<req> > feasible(n, vector<req>());
    value *couples = (value *)malloc(sizeof(value) * n * n);
    req *paths = (req *)malloc(sizeof(req) * 2 * K * n * n);
    value *drs = (value *)malloc(sizeof(value) * n * n);
    qos_t *qoss = (qos_t *)malloc(sizeof(qos_t) * n * n);
    //ProfilerStart("profile.log");

    vector<gsq_data> data(n_threads);
    vector<PRNG> gen(n_threads, PRNG(rd()));
    vector<set<coal, lex_coal> > vars(n_threads, set<coal, lex_coal>());

    for (uint i = 0; i < n_threads; ++i) {
        gen[i].seed(seed + i);
        data[i] = {
            n,
            PTR(reqs),
            PTR(steps),
            PTR(deltas),
            PTR(distance),
            PTR(time),
            .vars = &vars[i],
            couples,
            paths,
            drs,
            qoss,
            PTR(feasible),
            PTR(ur),
            PTR(ui),
            .gen = &gen[i],
            gtb,
            dr,
            cl,
            env_k
        };
    }

    // Precompute all couples' data (affordable)
    for (uint i = 0; i < n; ++i) {
        for (uint j = i + 1; j < n; ++j) {
            coal c = { .c = { 2, i, j }, 0 };
            compute_value(c, &data[0]);
            couples[i * n + j] = c.w;
            memcpy(paths + 2 * K * (i * n + j), c.p, sizeof(req) * 2 * K);
            drs[i * n + j] = c.dr;
            qoss[i * n + j] = c.qos;
            if (c.w > -FLT_MAX) {
                feasible[i].push_back(j);
                feasible[j].push_back(i);
            }
        }
    }

    // Sort feasible lists (needed for set operations)
    for (uint i = 0; i < n; ++i) {
        sort(feasible[i].begin(), feasible[i].end());
    }

    gettimeofday(&t1, nullptr);
    size_t gq_runs = 0;
    struct timeval t2;
    float elapsed;
    omp_set_num_threads(n_threads);

    // Greedy²
    do {
        gq_runs++;
        #pragma omp parallel for
        for (uint i = 0; i < n_threads; ++i) {
            greedy_squared(&data[i]);
        }
        gettimeofday(&t2, nullptr);
        elapsed = DELTAT(t2, t1);
    } while (elapsed <= gtb);

    //ProfilerStop();
    free(couples);
    free(paths);
    free(drs);
    free(qoss);

    // Collect all threads' results
    for (uint i = 1; i < n_threads; ++i) {
        vars[0].insert(vars[i].begin(), vars[i].end());
    }

    print_coals_csv(vars[0].begin(), vars[0].end());

    return EXIT_SUCCESS;
}
