#ifndef IO_HPP_
#define IO_HPP_
    
#include <iostream>     // std::cout
#include <vector>       // std::vector
#include <tuple>        // std::tuple

template <typename type>
void print_buf(const type *buf, int n, bool nl = true, const char *sep = ",") {

    while (n--) {
        std::cout << *(buf++);
        if (n) {
            std::cout << sep;
        }
    }
    if (nl) {
        std::cout << '\n';
    }
}

template <typename iterator>
void print_it(iterator begin, iterator end, const char *sep = ",") {

    iterator final_iter = end - 1;

    for (iterator it = begin; it != end; ++it) {
        std::cout << *it;
        if (it != final_iter) {
            std::cout << sep;
        }
    }
    std::cout << '\n';
}

template <typename iterable>
void print_coals(const iterable &coals) {

    for (auto coal : coals) {
        print_buf(coal.c + 1, coal.c[0], false);
        std::cout << " = " << coal.w << '\n';
    }
}

std::tuple<std::vector<int>, std::vector<int>, std::vector<int> > read_reqs(const char *filename);

std::vector<float> read_matrix(const char *filename, int nrows, int ncols);

#endif /* IO_HPP_ */
