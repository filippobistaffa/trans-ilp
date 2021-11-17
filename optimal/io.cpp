#include "io.hpp"

#include <fstream>      // std::ifstream
#include <vector>       // std::vector
#include <tuple>        // std::tuple
#include <climits>      // INT_MAX

std::tuple<std::vector<int>, std::vector<int>, std::vector<int> > read_reqs(const char *filename) {

    std::vector<int> reqs;
    std::vector<int> steps;
    std::vector<int> deltas;
    std::ifstream f(filename);
    std::string cell;

    while (getline(f, cell, ',')) {
        steps.push_back(stoi(cell));
        getline(f, cell, ',');
        reqs.push_back(stoi(cell));
        getline(f, cell);
        int val = stoi(cell);
        deltas.push_back(val < 0 ? INT_MAX : val);
    }

    f.close();
    return make_tuple(reqs, steps, deltas);
}

std::vector<float> read_matrix(const char *filename, int nrows, int ncols) {

    std::ifstream f(filename);
    std::vector<float> mat;
    std::string cell;

    for (int i = 0; i < nrows; ++i) {
        for (int i = 0; i < ncols - 1; ++i) {
            getline(f, cell, ',');
            mat.push_back(stof(cell));
        }
        getline(f, cell);
        mat.push_back(stof(cell));
    }

    f.close();
    return mat;
}
