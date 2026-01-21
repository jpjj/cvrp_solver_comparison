import time
import vrplib
from pathlib import Path
from cvrp_solver_comparison.domain.models import Instance, Solution
import polars as pl

from cvrp_solver_comparison.domain.solver import create_solver
from cvrp_solver_comparison.domain.utils import validate
from datetime import datetime

instance_names = list(
    set(f.name.split(".")[0] for f in Path("data/X").iterdir() if f.is_file())
)

solver_names = ["pyvrp"]  # , 'ortools', 'vroom', 'timefold', 'rustvrp', 'pyhygese'
time_limits = [1, 2]
num_instances = 5

results = {
    "Instance": [],
    "Size": [],
    "Time Limit (s)": [],
    "Solver": [],
    "Solution Quality": [],
}


for name in instance_names[:num_instances]:
    instance = vrplib.read_instance(f"data/X/{name}.vrp")
    solution = vrplib.read_solution(f"data/X/{name}.sol")
    instance = Instance.model_validate(instance)
    best_solution = Solution.model_validate(solution)
    for time_limit in time_limits:
        solvers = {
            name: create_solver(method=name, time_limit=time_limit)
            for name in solver_names
        }
        for s_name, solver in solvers.items():
            tic = time.time()
            solution = solver(instance)
            toc = time.time()
            real_time = toc - tic
            if real_time > time_limit * 1.1:
                print(
                    f"Warning, solver {s_name} took {real_time:2f} s on instance {name} despite setting a time limit of {time_limit} s."
                )
            validate(solution=solution, instance=instance)
            results["Instance"].append(instance.name)
            results["Size"].append(len(instance.demand))
            results["Time Limit (s)"].append(time_limit)
            results["Solver"].append(s_name)
            results["Solution Quality"].append(solution.cost / best_solution.cost)

df = pl.DataFrame(results)
df.write_csv(f"data/benchmark_{datetime.now()}.csv")
