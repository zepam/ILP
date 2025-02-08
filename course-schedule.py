import csv
import pulp


## load files ##
# Load CourseInfo.csv
courses = []
with open('examples/CourseInfo.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        courses.append(row)

# Load CoursesThisQuarter.csv
courses_this_quarter = []
with open('examples/CoursesThisQuarter.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        courses_this_quarter.append({k.strip(): v.strip() for k, v in row.items()})

# Load InstructorPref.csv
instructor_prefs = {}
with open('examples/InstructorPref.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        instructor_prefs[row['instructor name']] = row

# Load ConflictCourses.txt
conflict_pairs = []
with open('examples/ConflictCourses.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line and not line.startswith('#'):  # Skip comments and empty lines
            conflict_pairs.append(line.split())


## decision variables and problem ##

# Define the problem
prob = pulp.LpProblem("Course_Scheduling", pulp.LpMaximize)

# Define decision variables
time_slots = range(100)  # Example: 100 time slots (30 minutes each)
course_names = [c['course_name'] for c in courses]  # List of valid course names
x = pulp.LpVariable.dicts("x", ((c['course_name'], t) for c in courses for t in time_slots), cat="Binary")
y = pulp.LpVariable.dicts("y", (c['course_name'] for c in courses), cat="Binary")

## objective function ##

# Objective function
prob += pulp.lpSum(y[c['course_name']] for c in courses)

## constraints ##
# course is scheduled once #
for c in courses:
    prob += pulp.lpSum(x[c['course_name'], t] for t in time_slots) == 1

# handle conflicts #
for pair in conflict_pairs:
    # Skip pairs where either course is not in course_names
    if pair[0] in course_names and pair[1] in course_names:
        for t in time_slots:
            prob += x[pair[0], t] + x[pair[1], t] <= 1
    else:
        print(f"Skipping conflict pair {pair} because one or both courses are not in CourseInfo.csv")

# instructor preferences #
for c in courses_this_quarter:
    instructor = c['instructor name']
    prefs = instructor_prefs.get(instructor, {})
    preferred_days = prefs.get('preferred days', '').split(',')
    preferred_start = prefs.get('preferred start time', '')
    preferred_end = prefs.get('preferred end time', '')

    # Constraint for preferred days
    if preferred_days and any(preferred_days):
        prob += pulp.lpSum(x[c['course name'], t] for t in time_slots if t in preferred_days) >= y[c['course name']]

    # Constraint for preferred start and end times
    if preferred_start and preferred_end:
        for t in time_slots:
            if t < preferred_start or t + int(c['session_length']) > preferred_end:
                prob += x[c['course name'], t] <= 1 - y[c['course name']]

## solve the problem ##
prob.solve()

# Print the results
for c in courses:
    for t in time_slots:
        if pulp.value(x[c['course_name'], t]) == 1:
            print(f"Course {c['course_name']} starts at time slot {t}")

## save the results ##
# Save schedule to schedule.csv
with open('schedule.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['course_name', 'start_time'])
    for c in courses:
        for t in time_slots:
            if pulp.value(x[c['course_name'], t]) == 1:
                writer.writerow([c['course_name'], t])

# Generate heatmap (example)
heatmap = {}
for c in courses:
    for t in time_slots:
        if pulp.value(x[c['course_name'], t]) == 1:
            day = t // 20  # Example: 20 time slots per day
            heatmap[day] = heatmap.get(day, 0) + 1

with open('heatMap.txt', 'w') as file:
    for day, count in heatmap.items():
        file.write(f"Day {day}: {count} courses\n")

# Collect the course and time slot data
formatted_data = []
for c in courses:
    for t in time_slots:
        if pulp.value(x[c['course_name'], t]) == 1:
            formatted_data.append((c['course_name'], t))

# Organize the data into columns for time slots 1-20, 21-40, etc.
columns = 5
slot_range = 20  # Each column covers 20 time slots
organized_data = []

# Initialize a dictionary to group courses by their time slot ranges
slot_groups = {i: [] for i in range(columns)}

# Group courses into their respective time slot ranges
for course, slot in formatted_data:
    column_index = (slot) // slot_range  # Determine which column the slot belongs to
    if column_index < columns:  # Ensure it fits within the 5 columns
        slot_groups[column_index].append(f"{course}, {slot}")

# sort slot_groups by time slot number 
for i in range(columns):
    slot_groups[i].sort(key=lambda x: int(x.split()[-1]))
    # Extract the time slot number from the string and sort accordingly
    for i in range(columns):
        slot_groups[i].sort(key=lambda x: int(x.split()[-1].strip(')')))
# Determine the maximum number of rows needed
max_rows = max(len(slot_groups[i]) for i in range(columns))

# Pad the groups with empty strings to ensure equal row length
for i in range(columns):
    slot_groups[i] += [""] * (max_rows - len(slot_groups[i]))

# Transpose the data into rows and columns
organized_data = list(zip(*[slot_groups[i] for i in range(columns)]))

# Write the formatted data to a CSV file
with open('schedule_formatted.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([f"Slots {i * slot_range + 1}-{(i + 1) * slot_range}" for i in range(columns)])  # Header
    writer.writerows(organized_data)

print("Formatted schedule saved to 'schedule_formatted.csv'.")

## formatted for days of the week ##

# Sample data with multiple IDs per time slot
#data = [(101, 1), (102, 1), (103, 3), (104, 21), (105, 21), (106, 40)]

# Function to convert time slot to day and time
def time_slot_to_day_time(time_slot):
    time_slot = int(time_slot)
    if 1 <= time_slot <= 20:
        day = "Monday"
        start_time = "08:30"
    elif 21 <= time_slot <= 40:
        day = "Tuesday"
        time_slot -= 20
        start_time = "08:30"
    else:
        return None, None

    # Calculate the time based on the time slot
    hours = 8 + (time_slot - 1) // 2
    minutes = 30 if (time_slot - 1) % 2 else 0
    time = f"{hours:02d}:{minutes:02d}"

    return day, time

# Organize the data into a schedule
schedule = {}
for id_num, time_slot_for_day in slot_groups.items():
    for time_slot in time_slot_for_day:
        if time_slot:
            t = time_slot.split(',')[1].strip()
            day, time = time_slot_to_day_time(t)
            if day and time:
                if day not in schedule:
                    schedule[day] = {}
                if time not in schedule[day]:
                    schedule[day][time] = []
                schedule[day][time].append(id_num)

# Print the schedule
for day in sorted(schedule.keys()):
    print(f"{day}:")
    for time in sorted(schedule[day].keys()):
        ids = ", ".join(f"{id_num}" for id_num in schedule[day][time])
        print(f"  {time} - {ids}")
    print()