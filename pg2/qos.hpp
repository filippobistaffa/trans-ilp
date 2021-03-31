#ifndef QOS_HPP_
#define QOS_HPP_

#include "params.h"
#include "types.hpp"
#include "qos_type.hpp"
#include <vector>
#include <algorithm>

__attribute__((always_inline)) inline
value travel_time(req a, req b, const req *p, uint n, const std::vector<value> &time) {

	value ret = 0;
	bool add = false;
	//printf("time[%u -> %u] = %.2f\n", a + 1, b + 1, time[a * Z + b]);

	for (uint i = 0; i < n; ++i) {
		if (add && p[i] == b) {
			return ret;
		}
		if (p[i] == a) {
			add = true;
		}
		if (add) {
			//printf("time[%u -> %u] = %.2f\n", p[i] + 1, p[i + 1] + 1, time[p[i] * Z + p[i + 1]]);
			ret += time[p[i] * Z + p[i + 1]];
		}
	}

	return ret;
}

__attribute__((always_inline)) inline
value pickup_time(req a, const req *p, uint n, const std::vector<value> &time) {

	value ret = 0;

	// index of a in p
	int idx_a = find(p, p + n, a) - p;

	for (uint i = 0; i < idx_a; ++i) {
		ret += time[p[i] * Z + p[i + 1]];
	}

	return ret;
}

// Include To-Be-Assigned (TBA) delay in QoS
#define QOS_TBA

using namespace std;

__attribute__((always_inline)) inline
qos_t compute_qos(coal c, const vector<req> &reqs, const vector<step> &steps, const vector<step> &deltas, const vector<value> &time) {

	//print_buf(c.c + 1, c.c[0], "Request IDs");
	//print_buf(c.p, 2 * c.c[0], "Path");
	qos_t qos;
	qos.qos_tot = 0;
	qos.n = c.c[0];
	for (uint i = 0; i < c.c[0]; ++i) {
		const req a = reqs[c.c[i + 1]] / Z;
		const req b = reqs[c.c[i + 1]] % Z;
		const value time_rs = travel_time(a, b, c.p, 2 * c.c[0], time);
		const value time_nors = time[a * Z + b];
		const uint icd_val = time_rs > time_nors ? time_rs - time_nors : 0;
		const value qos_val = (time_rs == 0 && time_nors == 0) ? 0 : icd_val / time_rs;
		qos.icd[i] = icd_val;
		qos.tbp[i] = pickup_time(a, c.p, 2 * c.c[0], time);
		qos.tba[i] = steps[c.c[i + 1]];
		qos.qos[i] = qos_val;
		//printf("%u -> %u: +%ds, +%.2f%% (%.0f, %.0f)\n", a, b, icd_val, 100 * qos_val, time_rs, time_nors);
	}
	const step max_t = *max_element(qos.tba, qos.tba + c.c[0]);
	for (uint i = 0; i < c.c[0]; ++i) {
		qos.tba[i] = max_t - qos.tba[i];
		#ifdef QOS_TBA
		qos.qos[i] += (value)qos.tba[i] / deltas[c.c[i + 1]];
		qos.qos[i] /= 2;
		#endif
		qos.qos_tot += qos.qos[i];
	}
	//cout << endl;
	return qos;
}

#endif /* QOS_HPP_ */
