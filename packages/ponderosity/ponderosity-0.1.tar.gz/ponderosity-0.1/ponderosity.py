
"""
Given values for various macronutrients in grams, determine the number of
food points represented.
"""
def calculate_food_points(protein=0.0,
                          carbs=0.0,
                          fat=0.0,
                          fiber=0.0,
                          alcohol=0.0,
                          sugar_alcohol=0.0):
    points = (
        (float(protein) / 10.9375)
        + (float(carbs) / 9.2105)
        + (float(fat) / 3.8889)
        + (float(alcohol) / 3.0147)
        - (float(fiber) / 12.5)
        - (float(sugar_alcohol) / 23.0263)
    )
    if points > 0:
        return int(round(points))
    else:
        return 0


"""
Given an age in years, a weight in kilograms and a height in meters,
determine the daily energy expenditure for a man in kCal.
"""
def calculate_male_daily_energy_expenditure(age, weight, height):
    return (
        864.0
        - (9.72 * float(age))
        + 1.12 * (14.2 * float(weight) + 503 * float(height))
    )


"""
Given an age in years, a weight in kilograms and a height in meters,
determine the daily energy expenditure for a woman in kCal.
"""
def calculate_female_daily_energy_expenditure(age, weight, height):
    return (
        387.0
        - (7.31 * float(age))
        + 1.14 * (10.9 * float(weight) + 660.7 * float(height))
    )


"""
Adjust a daily energy expenditure value to an arbitrary range that is
used in the target points calculation.
"""
def adjust_daily_energy_expenditure(expenditure):
    return 0.9 * float(expenditure) + 200.0


def _calculate_target_points(age, weight, height, exp_func):
    exp = exp_func(age, weight, height)
    adj = adjust_daily_energy_expenditure(exp)
    target = int(round(max(adj - 1000.0, 1000.0) / 35.0) - 11.0)
    return min(max(target, 26), 71)


"""
Given an age in years, a weight in kilograms and a height in meters,
determine the daily points target for a man.
"""
def calculate_male_target_points(age, weight, height):
    return _calculate_target_points(
        age,
        weight,
        height,
        calculate_male_daily_energy_expenditure,
    )


"""
Given an age in years, a weight in kilograms and a height in meters,
determine the daily points target for a man.
"""
def calculate_female_target_points(age, weight, height):
    return _calculate_target_points(
        age,
        weight,
        height,
        calculate_female_daily_energy_expenditure,
    )


"""
Given a number of calories expended, determine the corresponding
activity points.
"""
def calculate_activity_points(calories=0.0):
    return int(round(float(calories) / 70.0))
