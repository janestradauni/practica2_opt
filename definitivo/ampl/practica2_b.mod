set INTERSECTIONS;
set PATHS;
set FIXED within INTERSECTIONS;
set PROHIBITED within INTERSECTIONS;
set PATH_INTERSECTIONS within {PATHS, INTERSECTIONS};
set NEIGHBORS within {INTERSECTIONS, INTERSECTIONS};

param PATH_FLOW {PATHS} > 0;

var x {i in INTERSECTIONS} binary;
var y {p in PATHS} binary;

maximize total_flow:
    sum {p in PATHS} PATH_FLOW[p] * y[p];

subject to sensor_budget:
    sum {i in INTERSECTIONS} x[i] <= 15;

subject to detected_paths {p in PATHS}:
    sum {(p, i) in PATH_INTERSECTIONS} x[i] >= 2 * y[p];

subject to fixed_sensors {i in FIXED}:
    x[i] = 1;

subject to prohibited_sensors {i in PROHIBITED}:
    x[i] = 0;

subject to separated_sensors {(i, j) in NEIGHBORS}:
    x[i] + x[j] <= 1;
