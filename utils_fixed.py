# sample file for first test
# Changes from utils.py:
#
# calculate_average(numbers):
#   - Bug fix: Guard against None input — raises ValueError instead of crashing
#     with TypeError ("'NoneType' object is not iterable").
#   - Bug fix: Guard against empty list — raises ValueError instead of crashing
#     with ZeroDivisionError (division by zero when len(numbers) == 0).
#
# get_user_name(user):
#   - Bug fix: Guard against None user — raises ValueError instead of crashing
#     with TypeError ("'NoneType' object is not subscriptable").
#   - Bug fix: Guard against missing "name" key — raises ValueError instead of
#     crashing with KeyError.
#   - Bug fix: Guard against None value for "name" — raises ValueError instead
#     of crashing with AttributeError ("'NoneType' object has no attribute 'upper'").


def calculate_average(numbers):
    if numbers is None:
        raise ValueError("numbers must not be None")
    if len(numbers) == 0:
        raise ValueError("numbers must not be empty")
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def get_user_name(user):
    if user is None:
        raise ValueError("user must not be None")
    if "name" not in user:
        raise ValueError("user dict is missing the 'name' key")
    if user["name"] is None:
        raise ValueError("user['name'] must not be None")
    return user["name"].upper()
