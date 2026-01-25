from timefold.solver.score import ConstraintFactory, HardSoftScore, constraint_provider

from .domain import DistanceMatrix, Vehicle, Visit

VEHICLE_CAPACITY = "vehicleCapacity"
MINIMIZE_TRAVEL_TIME = "minimizeTravelTime"
SERVICE_FINISHED_AFTER_MAX_END_TIME = "serviceFinishedAfterMaxEndTime"


@constraint_provider
def define_constraints(factory: ConstraintFactory):
    return [
        # Hard constraints
        vehicle_capacity(factory),
        # Soft constraints
        minimize_travel_time(factory),
    ]


##############################################
# Hard constraints
##############################################


def vehicle_capacity(factory: ConstraintFactory):
    return (
        factory.for_each(Vehicle)
        .filter(lambda vehicle: vehicle.calculate_total_demand() > vehicle.capacity)
        .penalize(
            HardSoftScore.ONE_HARD,
            lambda vehicle: vehicle.calculate_total_demand() - vehicle.capacity,
        )
        .as_constraint(VEHICLE_CAPACITY)
    )


##############################################
# Soft constraints
##############################################


def minimize_travel_time(factory: ConstraintFactory):
    return (
        factory.for_each(Vehicle)
        .join(DistanceMatrix)
        .penalize(
            HardSoftScore.ONE_SOFT,
            lambda vehicle, distance_matrix: vehicle.calculate_total_driving_time_seconds(
                distance_matrix.matrix
            ),
        )
        .as_constraint(MINIMIZE_TRAVEL_TIME)
    )
