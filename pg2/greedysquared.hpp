#ifndef GREEDYSQUARED_HPP_
#define GREEDYSQUARED_HPP_

#include <algorithm>

#define PTR(VAR) .VAR = &VAR

struct gsq_data {

	// General data structures
	req n;
	vector<req> *reqs;
	vector<step> *steps;
	vector<step> *deltas;
	vector<value> *distance;
	vector<value> *time;
	set<coal, lex_coal> *vars;
	// Data structures for optimisations
	value *couples;
	req *paths;
	value *drs;
	qos_t *qoss;
	vector<vector<req> > *feasible;
	// Probabilistic behaviour
	uniform_real_distribution<> *ur;
	uniform_int_distribution<> *ui;
	PRNG *gen;
	// Parameters
	float gtb; // Generation time budget
	float dr; // Determinism rate
	uint cl; // Candidate list length
	float k; // Weight for environmental benefits
};

__attribute__((always_inline)) inline
void compute_value(coal &c, const gsq_data *data) {

	sort(c.c + 1, c.c + 1 + c.c[0]);
	req zones[2 * c.c[0]];
	step min_tpd = UINT_MAX;
	step max_t = 0;

	for (uint i = 0; i < c.c[0]; ++i) {
		const uint idx = c.c[i + 1];
		zones[2 * i] = (*data->reqs)[idx] / Z;
		zones[2 * i + 1] = (*data->reqs)[idx] % Z;
		step d = (*data->deltas)[idx];
		step t = (*data->steps)[idx];
		if (d != UINT_MAX && t + d < min_tpd) {
			min_tpd = t + d;
		}
		if (t > max_t) {
			max_t = t;
		}
	}

	if (min_tpd >= max_t) {
		const value dist_nors = singvalue(zones, c.c[0], &(*data->distance)[0]);
		const value dist_rs = srvalue(zones, c.c[0], c.p, &(*data->distance)[0]);
		const value dist_impr = (dist_nors == 0) ? 0 : ((dist_nors - dist_rs) / dist_nors);
		const value cong_nors = c.c[0];
		const value cong_rs = 1;
		const value cong_impr = (cong_nors - cong_rs) / cong_nors;
		c.qos = compute_qos(c, *data->reqs, *data->steps, *data->deltas, *data->time);
		c.w = data->k * c.c[0] * (2 * dist_impr + cong_impr) / 3 - (1.0 - data->k) * c.qos.qos_tot;
		c.dr = dist_nors - dist_rs;
	} else {
		c.w = -FLT_MAX;
	}

	//print_buf(c.c + 1, c.c[0], NULL, NULL, " = ");
	//printf("%f\n\n", c.w);
}

#define SETOP(OP, X, Y, R) (OP((X).begin(), (X).end(), (Y).begin(), (Y).end(), inserter((R), (R).begin())))
#define DELTAT(T2, T1) ((float)((T2).tv_usec - (T1).tv_usec) / 1e3 + ((T2).tv_sec - (T1).tv_sec) * 1e3) // Milliseconds

__attribute__((always_inline)) inline
void greedy_squared(const gsq_data *data) {

	coal bc; // Current best coalition
	vector<coal> cl; // Candidate list
	cl.reserve(data->cl); // Avoids reallocations
	vector<bool> available(data->n, true); // Marks available requests
	float elapsed;

	// Main greedy loop, do this until no positive car can be formed or time expired
	do {
		bc.w = 0;
		cl.clear();
		bool det = (*(data->ur))(*(data->gen)) <= data->dr;

		// Check all available couples
		for (uint i = 0; i < data->n; ++i) {
			if (available[i]) {
				for (uint j = i + 1; j < data->n; ++j) {
					if (available[j]) {
						coal c = { .c = { 2, i, j }, 0 };
						c.w = data->couples[i * data->n + j];
						memcpy(c.p, data->paths + 2 * K * (i * data->n + j), sizeof(req) * 2 * K);
						c.dr = data->drs[i * data->n + j];
						c.qos = data->qoss[i * data->n + j];
						//puts("Current");
						//print_buf(c.c + 1, c.c[0], nullptr, nullptr, " = ");
						//printf("%f\n", c.w);
						if (det) {
							if (c.w > bc.w) {
								bc = c;
							}
						} else {
							//puts("CL before");
							//print_coals(cl.begin(), cl.end());
							if (cl.size() == data->cl) {
								if (c.w > cl.front().w) {
									pop_heap(cl.begin(), cl.end(), greater_w());
									cl[data->cl - 1] = c;
									push_heap(cl.begin(), cl.end(), greater_w());
								}
							} else {
								cl.push_back(c);
								push_heap(cl.begin(), cl.end(), greater_w());
							}
							//puts("CL after");
							//print_coals(cl.begin(), cl.end());
						}
					}
				}
			}
		}

		if (!det && cl.size()) {
			//puts("Random behaviour");
			const uint idx = (*(data->ui))(*(data->gen)) % cl.size();
			bc = cl[idx];
		}

		if (bc.w > 0) { // Positive couple found

			vector<req> orig_int((*(data->feasible))[bc.c[1]]), new_int;
			req added = bc.c[2];

			for (uint k = 2; k < K; ++k) {

				coal c = bc;
				for (uint i = 0; i < c.c[0]; ++i) {
					const uint idx = c.c[i + 1];
					available[idx] = false;
				}

				//printf("Expanding ");
				//print_buf(c.c + 1, c.c[0], nullptr, nullptr, " = ");
				//printf("%f\n", c.w);

				cl.clear();
				bool better = false;
				det = (*(data->ur))(*(data->gen)) <= data->dr;
				SETOP(set_intersection, orig_int, (*(data->feasible))[added], new_int);

				//puts("Original");
				//print_it(orig_int.begin(), orig_int.end());
				//printf("%u feasible list\n", added);
				//print_it((*(data->feasible))[added].begin(), (*(data->feasible))[added].end());
				//puts("New");
				//print_it(new_int.begin(), new_int.end());

				for (req i : new_int) {
					if (available[i]) {

						coal nc = c;
						nc.c[nc.c[0] + 1] = i;
						nc.c[0]++;
						compute_value(nc, data);

						if (det) {
							if (nc.w > bc.w) {
								better = true;
								bc = nc;
							}
						} else {
							//puts("CL before");
							//print_coals(cl.begin(), cl.end());
							if (cl.size() == data->cl) {
								if (nc.w > cl.front().w) {
									pop_heap(cl.begin(), cl.end(), greater_w());
									cl[data->cl - 1] = nc;
									push_heap(cl.begin(), cl.end(), greater_w());
								}
							} else {
								cl.push_back(nc);
								push_heap(cl.begin(), cl.end(), greater_w());
							}
							//puts("CL after");
							//print_coals(cl.begin(), cl.end());
						}
					}
				}

				if (!det && cl.size()) {
					//puts("Random behaviour");
					const uint idx = (*(data->ui))(*(data->gen)) % cl.size();
					if (cl[idx].w > bc.w) {
						better = true;
						bc = cl[idx];
					}
				}

				if (better) {
					added = bc.c[bc.c[0]];
					orig_int = new_int;
					new_int.clear();
				} else {
					break;
				}
			}
		}

		if (bc.w > 0) {
			//printf("New variable: ");
			//print_buf(bc.c + 1, bc.c[0], nullptr, nullptr, " = ");
			//printf("%f\n", bc.w);
			data->vars->insert(bc);
		}

		struct timeval t2;
		gettimeofday(&t2, nullptr);
		elapsed = DELTAT(t2, t1);

	} while (bc.w > 0 && elapsed <= data->gtb);
}

#endif /* GREEDYSQUARED_HPP_ */
