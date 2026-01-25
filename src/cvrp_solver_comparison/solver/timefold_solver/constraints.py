from timefold.solver.score import (
    ConstraintFactory,
    ConstraintCollectors,
    HardSoftScore,
    constraint_provider,
)

from .domain import DistanceMatrix, Visit

VEHICLE_CAPACITY = "vehicleCapacity"
MINIMIZE_TRAVEL_TIME = "minimizeTravelTime"
SERVICE_FINISHED_AFTER_MAX_END_TIME = "serviceFinishedAfterMaxEndTime"


@constraint_provider
def define_constraints(factory: ConstraintFactory):
    return [
        # Hard constraints
        vehicle_capacity(factory),
        # Soft constraints
        *minimize_travel_time(factory),
    ]


##############################################
# Hard constraints
##############################################


def vehicle_capacity(factory: ConstraintFactory):
    return (
        factory.for_each(Visit)
        .filter(lambda visit: visit.vehicle is not None)
        .group_by(
            lambda visit: visit.vehicle,
            ConstraintCollectors.sum(lambda visit: visit.demand),
        )
        .filter(lambda vehicle, total_demand: total_demand > vehicle.capacity)
        .penalize(
            HardSoftScore.ONE_HARD,
            lambda vehicle, total_demand: total_demand - vehicle.capacity,
        )
        .as_constraint(VEHICLE_CAPACITY)
    )


##############################################
# Soft constraints
##############################################


def minimize_travel_time(factory: ConstraintFactory):
    # Penalize arc from depot to first visit
    depot_to_first = (
        factory.for_each(Visit)
        .filter(
            lambda visit: visit.vehicle is not None and visit.previous_visit is None
        )
        .join(DistanceMatrix)
        .penalize(
            HardSoftScore.ONE_SOFT,
            lambda visit, dm: dm.matrix[visit.vehicle.home_location][visit.location],
        )
        .as_constraint("depotToFirstVisit")
    )

    # Penalize arcs between consecutive visits
    visit_to_visit = (
        factory.for_each(Visit)
        .filter(lambda visit: visit.previous_visit is not None)
        .join(DistanceMatrix)
        .penalize(
            HardSoftScore.ONE_SOFT,
            lambda visit, dm: dm.matrix[visit.previous_visit.location][visit.location],
        )
        .as_constraint("visitToVisit")
    )

    # Penalize arc from last visit back to depot
    last_to_depot = (
        factory.for_each(Visit)
        .filter(lambda visit: visit.vehicle is not None and visit.next_visit is None)
        .join(DistanceMatrix)
        .penalize(
            HardSoftScore.ONE_SOFT,
            lambda visit, dm: dm.matrix[visit.location][visit.vehicle.home_location],
        )
        .as_constraint("lastVisitToDepot")
    )

    return [depot_to_first, visit_to_visit, last_to_depot]
