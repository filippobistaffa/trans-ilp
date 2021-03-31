#ifndef IO_HPP_
#define IO_HPP_

// Parameters

// Enable coloured output
//#define COLOURS

// Print input
//#define PRINT_INPUT

// Print ILP variables
#define PRINT_VARS

// Headers
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

using namespace std;

#include "types.hpp"

// Prints the content of a buffer
template <typename type>
__attribute__((always_inline)) inline
void print_buf_sep(const type *buf, unsigned n, const char *sep = ",") {

	while (n--) {
		cout << *(buf++);
		if (n) {
			cout << sep;
		}
	}
	cout << endl;
}

// Prints the content of an iterable type
template <typename iterator>
__attribute__((always_inline)) inline
void print_it(iterator begin, iterator end, const char *name = nullptr, const char *format = nullptr, const char *after = nullptr) {

	if (name) printf("%s = [ ", name);
	else printf("[ ");
	for (iterator it = begin; it != end; ++it) {
		if (format) { printf(format, *it); printf(" "); }
		else cout << *it << " ";
	}
	printf("]%s", (after) ? after : "\n");
}

// Prints the content of an iterable type with a given separator
template <typename iterator>
__attribute__((always_inline)) inline
void print_it_sep(iterator begin, iterator end, const char *sep = ",") {

	iterator final_iter = end - 1;

	for (iterator it = begin; it != end; ++it) {
		cout << *it;
		if (it != final_iter) {
			cout << sep;
		}
	}
	cout << endl;
}

// Prints the content of an iterable type
template <typename iterator>
__attribute__((always_inline)) inline
void print_mat(iterator begin, iterator end, uint ncols, const char *name = nullptr, const char *format = nullptr) {

	if (name) printf("%s = \n", name);
	uint i = 1;
	for (iterator it = begin; it != end; ++it, ++i) {
		if (i == 1) printf("[ ");
		if (format) { printf(format, *it); printf(" "); }
		else cout << *it << " ";
		if (i == ncols) {
			cout << "]" << endl;
			i = 0;
		}
	}
}

template <typename iterator>
__attribute__((always_inline)) inline
void print_coals(iterator begin, iterator end) {

        for (iterator it = begin; it != end; ++it) {
                print_buf(it->c + 1, it->c[0], nullptr, nullptr, " = ");
                cout << it->w << endl;
        }
}

template <typename iterator>
__attribute__((always_inline)) inline
void print_coals_csv(iterator begin, iterator end) {

        for (iterator it = begin; it != end; ++it) {
                cout << it->w << ",";
                print_buf_sep(it->c + 1, it->c[0]);
        }
}

void read_reqs(const char *filename, vector<req> &reqs, vector<step> &steps, vector<step> &deltas);

void read_matrix(const char *filename, uint nrows, uint ncols, vector<value> &mat);

#endif /* IO_HPP_ */
