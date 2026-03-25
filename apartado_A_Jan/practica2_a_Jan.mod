# practica2_a.mod

set INTERSECTIONS;
set PATHS;

set FIXED within INTERSECTIONS;
set PROHIBITED within INTERSECTIONS;

set PATH_INTERSECTIONS within {PATHS, INTERSECTIONS};

param path_flow {PATHS} >= 0;

var x {i in INTERSECTIONS} binary;
var y {p in PATHS} binary;

maximize total_flow:
    sum {p in PATHS} path_flow[p] * y[p];

subject to max_sensors:
    sum {i in INTERSECTIONS} x[i] <= 15;

subject to detect_path {p in PATHS}:
    sum {(p,i) in PATH_INTERSECTIONS} x[i] >= 2 * y[p];

subject to fixed_nodes {i in FIXED}:
    x[i] = 1;

subject to prohibited_nodes {i in PROHIBITED}:
    x[i] = 0;
