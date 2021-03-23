#include "cpp_oracle.hpp"

float cpp_oracle(const uint32_t s, const uint32_t *_c, const uint32_t n, const uint32_t *_reqs, const uint32_t *_steps, const uint32_t *_deltas, const float *_distance, const float *_time) {

        std::vector<req> reqs(n);
        reqs.assign(_reqs, _reqs + n);
        std::vector<step> steps(n);
        steps.assign(_steps, _steps + n);
        std::vector<step> deltas(n);
        deltas.assign(_deltas, _deltas + n);
        std::vector<value> distance(Z * Z);
        distance.assign(_distance, _distance + Z * Z);
        std::vector<value> time(Z * Z);
        time.assign(_time, _time + Z * Z);
        const float env_k = 0.5;
        cv_data data = { n, PTR(reqs), PTR(steps), PTR(deltas), PTR(distance), PTR(time), env_k };
        coal c;
        c.c[0] = s;
        std::copy(_c, _c + s, c.c + 1);
        compute_value(c, &data);
        return c.w;
}
