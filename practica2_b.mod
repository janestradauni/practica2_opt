set INTERSECTIONS;
set PATHS;
set FIXED within INTERSECTIONS;
set PROHIBITED within INTERSECTIONS;
set PATH_INTERSECTIONS within {PATHS, INTERSECTIONS};
set NEIGHBORS within {INTERSECTIONS, INTERSECTIONS};

param PATH_FLOW {PATHS} > 0;

var x {INTERSECTIONS} binary;
var y {PATHS} binary;

maximize total_flow:
    sum {p in PATHS} PATH_FLOW[p] * y[p];

s.t. sensor_budget:
    sum {i in INTERSECTIONS} x[i] <= 15;

s.t. fixed_sensors {i in FIXED}:
    x[i] = 1;

s.t. prohibited_sensors {i in PROHIBITED}:
    x[i] = 0;

s.t. detected_paths {p in PATHS}:
    sum {i in INTERSECTIONS: (p, i) in PATH_INTERSECTIONS} x[i] >= 2 * y[p];

s.t. separated_sensors {(i, j) in NEIGHBORS}:
    x[i] + x[j] <= 1;
