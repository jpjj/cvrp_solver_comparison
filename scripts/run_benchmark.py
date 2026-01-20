import time
import vrplib
from pathlib import Path
from cvrp_solver_comparison.domain.models import Instance, Solution
import polars as pl

from cvrp_solver_comparison.domain.solver import create_solver


instance_names = list(
    set(f.name.split(".")[0] for f in Path("data/X").iterdir() if f.is_file())
)

solver_names = ["pyvrp"]  # , 'ortools', 'vroom', 'timefold', 'rustvrp', 'pyhygese'
time_limit = 1
num_instances = 5

results = {}

solvers = {
    name: create_solver(method=name, time_limit=time_limit) for name in solver_names
}

for name in instance_names[:num_instances]:
    instance = vrplib.read_instance(f"data/X/{name}.vrp")
    solution = vrplib.read_solution(f"data/X/{name}.sol")
    instance = Instance.model_validate(instance)
    best_solution = Solution.model_validate(solution)
    results[instance.name] = {}
    for s_name, solver in solvers.items():
        tic = time.time()
        solution = solver(instance)
        toc = time.time()
        real_time = toc - tic
        if real_time * 1.1 < time_limit:
            print(
                f"Warning, solver {s_name} took {real_time:2f} s on instance {name} despite setting a time limit of {time_limit} s."
            )
        results[instance.name] = solution.cost / best_solution.cost

df = pl.DataFrame(results)
df.write_csv(f"data/benchmark_{time.now()}.csv")
