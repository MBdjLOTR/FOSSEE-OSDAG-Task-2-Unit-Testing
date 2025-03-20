import pytest
from bolted_lap_joint import design_lap_joint, calculate_bolt_strength

# Define test cases
loads = range(0, 101, 10)  # Load P in kN (0 to 100 kN in steps of 10)
thicknesses = [6, 8, 10, 12, 16, 20, 24]  # Thicknesses t1 and t2 in mm
plate_width = 150  # Width of the plates in mm (fixed for simplicity)
plate_grades = ["E250", "E275", "E300", "E350", "E410", "E450", "E500", "E550"]  # Plate grades

# Test function to check if the design has at least two bolts
@pytest.mark.parametrize("P", loads)
@pytest.mark.parametrize("t1", thicknesses)
@pytest.mark.parametrize("t2", thicknesses)
@pytest.mark.parametrize("plate_grade", plate_grades)
def test_minimum_bolts(P, t1, t2, plate_grade):
    """
    Test that the design_lap_joint function returns a design with at least two bolts
    for any load P, thicknesses t1, t2, and plate grade.
    """
    try:
        design = design_lap_joint(P, plate_width, t1, t2, plate_grade)
        assert design["number_of_bolts"] >= 2, f"Design with P={P} kN, t1={t1} mm, t2={t2} mm, grade={plate_grade} has fewer than 2 bolts"
    except ValueError as e:
        # If no design is found, ensure it's not due to insufficient bolts
        assert False, f"No design found for P={P} kN, t1={t1} mm, t2={t2} mm, grade={plate_grade}: {e}"

# Optional: Test the calculate_bolt_strength function
@pytest.mark.parametrize("bolt_grade, expected_fu, expected_fy", [
    (3.6, 360, 216),
    (4.6, 460, 276),
    (5.8, 580, 464),
    (8.8, 800, 640),
    (10.9, 1000, 900),
])
def test_calculate_bolt_strength(bolt_grade, expected_fu, expected_fy):
    """
    Test the calculate_bolt_strength function for correctness.
    """
    fu, fy = calculate_bolt_strength(bolt_grade)
    assert fu == expected_fu, f"Expected ultimate strength {expected_fu}, got {fu}"
    assert fy == expected_fy, f"Expected yield strength {expected_fy}, got {fy}"
