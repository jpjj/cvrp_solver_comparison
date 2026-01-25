from dataclasses import dataclass
from timefold.solver import SolverStatus
from timefold.solver.score import HardSoftScore
from timefold.solver.domain import (
    planning_entity,
    PlanningId,
    planning_solution,
    InverseRelationShadowVariable,
    PreviousElementShadowVariable,
    NextElementShadowVariable,
    PlanningListVariable,
    PlanningEntityCollectionProperty,
    ProblemFactProperty,
    ValueRangeProvider,
    PlanningScore,
)

from typing import Annotated, Optional
from pydantic import Field, computed_field

from cvrp_solver_comparison.solver.timefold_solver.json_serialization import (
    IdListSerializer,
    IdSerializer,
    VehicleValidator,
    VisitListValidator,
    VisitValidator,
    ScoreSerializer,
    ScoreValidator,
)


@dataclass
class DistanceMatrix:
    id: Annotated[str, PlanningId]
    matrix: list[list[int]]

    def get_distance(self, from_loc: int, to_loc: int) -> int:
        return self.matrix[from_loc][to_loc]


@planning_entity
@dataclass
class Visit:
    id: Annotated[int, PlanningId]
    name: str
    location: int
    demand: int
    vehicle: Annotated[
        Optional["Vehicle"],
        InverseRelationShadowVariable(source_variable_name="visits"),
        IdSerializer,
        VehicleValidator,
        Field(default=None),
    ]
    previous_visit: Annotated[
        Optional["Visit"],
        PreviousElementShadowVariable(source_variable_name="visits"),
        IdSerializer,
        VisitValidator,
        Field(default=None),
    ]
    next_visit: Annotated[
        Optional["Visit"],
        NextElementShadowVariable(source_variable_name="visits"),
        IdSerializer,
        VisitValidator,
        Field(default=None),
    ]

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"Visit({self.id})"


@planning_entity
@dataclass
class Vehicle:
    id: Annotated[str, PlanningId]
    capacity: int
    home_location: int
    visits: Annotated[
        list[Visit],
        PlanningListVariable,
        IdListSerializer,
        VisitListValidator,
        Field(default_factory=list),
    ]

    @computed_field
    @property
    def total_demand(self) -> int:
        return self.calculate_total_demand()

    @computed_field
    @property
    def total_driving_time_seconds(self) -> int:
        return self.calculate_total_driving_time_seconds()

    def calculate_total_demand(self) -> int:
        total_demand = 0
        for visit in self.visits:
            total_demand += visit.demand
        return total_demand

    def calculate_total_driving_time_seconds(self, matrix) -> int:
        if len(self.visits) == 0:
            return 0
        total_driving_time_seconds = 0
        previous_location = self.home_location

        for visit in self.visits:
            total_driving_time_seconds += matrix[previous_location][visit.location]

            previous_location = visit.location

        total_driving_time_seconds += matrix[previous_location][self.home_location]
        return total_driving_time_seconds

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"Vehicle({self.id})"


@planning_solution
@dataclass
class VehicleRoutePlan:
    name: str
    vehicles: Annotated[list[Vehicle], PlanningEntityCollectionProperty]
    visits: Annotated[list[Visit], PlanningEntityCollectionProperty, ValueRangeProvider]
    distance_matrix: Annotated[DistanceMatrix, ProblemFactProperty]
    score: Annotated[
        Optional[HardSoftScore],
        PlanningScore,
        ScoreSerializer,
        ScoreValidator,
        Field(default=None),
    ]
    solver_status: Annotated[Optional[SolverStatus], Field(default=None)]

    @computed_field
    @property
    def total_driving_time_seconds(self) -> int:
        out = 0
        for vehicle in self.vehicles:
            out += vehicle.total_driving_time_seconds
        return out

    def __str__(self):
        return f"VehicleRoutePlan(name={self.id}, vehicles={self.vehicles}, visits={self.visits})"
