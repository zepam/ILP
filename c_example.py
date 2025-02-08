import pandas as pd
import pulp

# Load data from CSV files
course_info = pd.read_csv("examples/CourseInfo.csv")
courses_this_quarter = pd.read_csv("examples/CoursesThisQuarter.csv")
instructor_pref = pd.read_csv("examples/InstructorPref.csv")

# Define constants
TIME_SLOTS = list(range(20))  # 20 time slots per day
DAYS = ["M", "T", "W", "Th", "F"]

# Create a mapping from course name to its details
course_details = {row["course_name"]: row for _, row in course_info.iterrows() if row["course_name"][0].isdigit()}

# Create a mapping from instructor name to their preferences
instructor_preferences = {row["instructor name"]: row for _, row in instructor_pref.iloc[1:].iterrows()}

# Define the ILP problem
prob = pulp.LpProblem("Course_Scheduling", pulp.LpMaximize)

# Decision Variables
# 1. x_c,t: 1 if course c starts at time slot t, 0 otherwise
x = pulp.LpVariable.dicts("x", ((c, t) for c in course_info["course_name"] for t in TIME_SLOTS), cat="Binary")

# 2. y_c: 1 if course c meets its instructor's preferences, 0 otherwise
y = pulp.LpVariable.dicts("y", (c for c in course_info["course_name"]), cat="Binary")

# # 3. z_c1,c2: 1 if courses c1 and c2 overlap in time, 0 otherwise
# conflict_courses = set()
# for _, row in course_info.iterrows():
#     if pd.notna(row["ConflictCourses"]):
#         conflict_courses.add(tuple(sorted(row["ConflictCourses"].split(","))))
# z = pulp.LpVariable.dicts("z", conflict_courses, cat="Binary")

# 4. d_c,d: 1 if course c is scheduled on day d, 0 otherwise
d = pulp.LpVariable.dicts("d", ((c, day) for c in course_info["course_name"] for day in DAYS), cat="Binary")

# 5. s_c: Start time of course c (in time slots)
s = pulp.LpVariable.dicts("s", (c for c in course_info["course_name"]), lowBound=0, upBound=99, cat="Integer")

# 6. e_c: End time of course c (in time slots)
e = pulp.LpVariable.dicts("e", (c for c in course_info["course_name"]), lowBound=0, upBound=99, cat="Integer")

# Objective Function: Maximize the number of courses that meet their instructors' preferences
prob += pulp.lpSum(y[c] for c in course_info["course_name"])

# Constraints
for _, row in course_info.iterrows():
    course = row["course_name"]
    length = row["session_length"]
    sessions_per_week = row["num_sessions_per_week"]
    must_on_days = row["mustOnDays"]
    start_time = row["start_time"]
    end_time = row["end_time"]

    # Constraint: Each course must start at exactly one time slot
    prob += pulp.lpSum(x[course, t] for t in TIME_SLOTS) == 1

    # Constraint: Link x_c,t to s_c (start time of course c)
    prob += s[course] == pulp.lpSum(t * x[course, t] for t in TIME_SLOTS)

    # Constraint: Link s_c to e_c (end time of course c)
    prob += e[course] == s[course] + (length // 30)

    # Constraint: Courses must meet on specified days
    if pd.notna(must_on_days):
        allowed_days = must_on_days.split(",")
        for day in DAYS:
            if day not in allowed_days:
                prob += d[course, day] == 0

    # Constraint: Courses must start and end within specified times
    if pd.notna(start_time):
        start_slot = int(start_time.split(":")[0]) * 2 + int(start_time.split(":")[1]) // 30
        prob += s[course] >= start_slot

    if pd.notna(end_time):
        end_slot = int(end_time.split(":")[0]) * 2 + int(end_time.split(":")[1]) // 30
        prob += e[course] <= end_slot

    # Constraint: Block scheduling policy (R3)
    if length == 50:
        allowed_start_slots = [8.5 * 2, 9.5 * 2, 10.5 * 2, 11.5 * 2, 12.5 * 2, 13.5 * 2]
        prob += pulp.lpSum(x[course, t] for t in TIME_SLOTS if t not in allowed_start_slots) == 0
    elif length == 80:
        allowed_start_slots = [8.5 * 2, 10 * 2, 11.5 * 2, 13 * 2]
        prob += pulp.lpSum(x[course, t] for t in TIME_SLOTS if t not in allowed_start_slots) == 0
    elif length == 110:
        allowed_start_slots = [8.5 * 2, 10.5 * 2, 12.5 * 2, 13.5 * 2]
        prob += pulp.lpSum(x[course, t] for t in TIME_SLOTS if t not in allowed_start_slots) == 0

    # Constraint: Days of the class (R4)
    if sessions_per_week == 2:
        prob += pulp.lpSum(d[course, day] for day in DAYS if day not in ["M", "W", "T", "Th"]) == 0
    elif sessions_per_week == 3:
        prob += pulp.lpSum(d[course, day] for day in DAYS if day not in ["M", "W", "F"]) == 0

    # Constraint: Instructor preferences (P1-P3)
    instructor = courses_this_quarter[courses_this_quarter["course name"] == course]["instructor name"].values[0]
    pref = instructor_preferences[instructor]

    if pd.notna(pref["preferred days"]):
        preferred_days = pref["preferred days"].split(",")
        prob += pulp.lpSum(d[course, day] for day in DAYS if day not in preferred_days) == 0

    if pd.notna(pref["preferred start time"]):
        preferred_start = int(pref["preferred start time"].split(":")[0]) * 2 + int(pref["preferred start time"].split(":")[1]) // 30
        prob += s[course] >= preferred_start

    if pd.notna(pref["preferred end time"]):
        preferred_end = int(pref["preferred end time"].split(":")[0]) * 2 + int(pref["preferred end time"].split(":")[1]) // 30
        prob += e[course] <= preferred_end

    # Constraint: Same-day requirement (R11)
    if pref["sameDay"] == 1:
        for other_course in course_info[course_info["course_name"] != course]["course_name"]:
            if courses_this_quarter[courses_this_quarter["course name"] == other_course]["instructor name"].values[0] == instructor:
                prob += pulp.lpSum(d[course, day] for day in DAYS) == pulp.lpSum(d[other_course, day] for day in DAYS)

# Solve the problem
prob.solve()

# Output the results
if pulp.LpStatus[prob.status] == "Optimal":
    print("Optimal solution found!")
    for c in course_info["course_name"]:
        for t in TIME_SLOTS:
            if pulp.value(x[c, t]) == 1:
                print(f"Course {c} starts at time slot {t} on day {DAYS[t // 20]}")
else:
    print("No optimal solution found.")