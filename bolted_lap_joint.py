import math

# Constants and available options
BOLT_DIAMETERS = [10, 12, 16, 20, 24]  # Bolt diameters in mm
BOLT_GRADES = [3.6, 4.6, 4.8, 5.6, 5.8, 6.8, 8.8, 10.9]  # Bolt grades
PLATE_GRADES = ["E250", "E275", "E300", "E350", "E410", "E450", "E500", "E550"]  # Plate grades

# Mapping of plate grades to yield and ultimate strengths (fy, fu) in MPa
PLATE_STRENGTHS = {
    "E250": (250, 410),
    "E275": (275, 440),
    "E300": (300, 470),
    "E350": (350, 510),
    "E410": (410, 550),
    "E450": (450, 590),
    "E500": (500, 650),
    "E550": (550, 700),
}

# Safety factor for bolt shear capacity
SAFETY_FACTOR = 1.33  # Corresponds to 0.75 in the utilization ratio

def calculate_bolt_strength(bolt_grade):
    """
    Calculate the ultimate tensile strength (fu) and yield strength (fy) of a bolt based on its grade.
    :param bolt_grade: Bolt grade (e.g., 4.6, 5.8)
    :return: Tuple of (fu, fy) in MPa
    """
    fu = int(bolt_grade) * 100  # Ultimate tensile strength
    fy = (bolt_grade - int(bolt_grade)) * fu  # Yield strength
    return fu, fy

def calculate_shear_capacity(fy, A_bolt):
    """
    Calculate the shear capacity of a bolt as per IS 800:2007.
    :param fy: Yield strength of the bolt in MPa
    :param A_bolt: Cross-sectional area of the bolt in mm²
    :return: Shear capacity in N
    """
    # Simplified formula for shear capacity (V_b = 0.6 * fy * A_bolt)
    return 0.6 * fy * A_bolt

def calculate_bearing_capacity(fu_plate, t, d):
    """
    Calculate the bearing capacity of a bolt as per IS 800:2007.
    :param fu_plate: Ultimate strength of the plate in MPa
    :param t: Total thickness of the plates in mm
    :param d: Diameter of the bolt in mm
    :return: Bearing capacity in N
    """
    # Simplified formula for bearing capacity (V_dpb = 2.5 * fu_plate * t * d)
    return 2.5 * fu_plate * t * d

def design_lap_joint(P, w, t1, t2, plate_grade="E410"):
    """
    Design a bolted lap joint connecting two plates.
    :param P: Tensile force in kN
    :param w: Width of the plates in mm
    :param t1: Thickness of plate 1 in mm
    :param t2: Thickness of plate 2 in mm
    :param plate_grade: Grade of the steel plate (default is E410)
    :return: Dictionary of design parameters and results
    """
    P_N = P * 1000  # Convert tensile force to Newtons
    best_design = None
    min_length = float('inf')

    # Check if the plate grade is valid
    if plate_grade not in PLATE_STRENGTHS:
        raise ValueError(f"Invalid plate grade: {plate_grade}. Available grades are {list(PLATE_STRENGTHS.keys())}")

    # Get plate strengths
    fy_plate, fu_plate = PLATE_STRENGTHS[plate_grade]

    # Iterate through all combinations of bolt diameters and grades
    for d in BOLT_DIAMETERS:
        for GB in BOLT_GRADES:
            # Calculate bolt strength
            fu_bolt, fy_bolt = calculate_bolt_strength(GB)
            A_bolt = math.pi * (d / 2) ** 2  # Cross-sectional area of the bolt

            # Calculate shear capacity of one bolt
            V_b = calculate_shear_capacity(fy_bolt, A_bolt)

            # Calculate required number of bolts
            N_b = math.ceil(P_N / (V_b / SAFETY_FACTOR))

            # Skip designs with fewer than 2 bolts
            if N_b < 2:
                continue

            # Calculate detailing distances
            e = d + 5  # End distance
            p = d + 10  # Pitch distance
            g = w / 2  # Gauge distance

            # Calculate length of the connection
            length_of_connection = w + 2 * e

            # Calculate bearing capacity
            t_total = t1 + t2  # Total thickness of plates
            V_dpb = calculate_bearing_capacity(fu_plate, t_total, d)

            # Calculate utilization ratio
            utilization_ratio = P_N / (N_b * V_b / SAFETY_FACTOR)

            # Check if this design is better (minimizes length and utilization ratio <= 1)
            if utilization_ratio <= 1 and length_of_connection < min_length:
                min_length = length_of_connection
                best_design = {
                    "bolt_diameter": d,
                    "bolt_grade": GB,
                    "number_of_bolts": N_b,
                    "pitch_distance": p,
                    "gauge_distance": g,
                    "end_distance": e,
                    "edge_distance": e,
                    "number_of_rows": 1,  # Simple design assumption
                    "number_of_columns": N_b,
                    "hole_diameter": d + 2,  # Hole diameter is slightly larger than the bolt
                    "strength_of_connection": N_b * V_b / SAFETY_FACTOR,
                    "yield_strength_plate_1": fy_plate,
                    "yield_strength_plate_2": fy_plate,
                    "length_of_connection": length_of_connection,
                    "efficiency_of_connection": utilization_ratio,
                }

    if best_design is None:
        raise ValueError("No suitable design found that meets the requirements.")

    return best_design
