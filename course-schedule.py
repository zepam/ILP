#from pulp import *

def read_courses_this_quarter(file_path):
    courses = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line
        for line in file:
            # skip if line starts with ,,,,,
            if line.startswith(','):
                continue
            #course_name, instructor_name, days, start_time, end_time, note = line.strip().split(',')
            parts = line.strip().split(',')
            course_name = parts[0]
            instructor_name = parts[1]
            days = parts[2]
            start_time = parts[3]
            end_time = parts[4]
            note = ','.join(parts[5:])
            course = {
                'course_name': course_name,
                'instructor_name': instructor_name,
                'days': days,
                'start_time': start_time,
                'end_time': end_time,
                'note': note
            }
            courses.append(course)
    return courses

def read_course_information(file_path):
    course_info = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line
        for line in file:
            # skip if line starts with ,,,,,
            if line.startswith(','):
                continue
            parts = line.strip().split(',')
            course_name = parts[0]
            session_length = parts[1]
            num_sessions_per_week = parts[2]
            is_large_class = parts[3]
            ten_percent_rule_exempted_class = parts[4]
            ten_percent_rule_exempted_TA = parts[5]
            mustOnDays = parts[6]
            start_time = parts[7]
            end_time = parts[8]
            course = {
                'course_name': course_name,
                'session_length': session_length,
                'num_sessions_per_week': num_sessions_per_week,
                'is_large_class': is_large_class,
                '10_percent_rule_exempted_class': ten_percent_rule_exempted_class,
                '10_percent_rule_exempted_TA': ten_percent_rule_exempted_TA,
                'mustOnDays': mustOnDays,
                'start_time': start_time,
                'end_time': end_time
            }
            course_info.append(course)
    return course_info

def read_instructor_information(file_path):
    course_info = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line
        for line in file:
            #instructor_name, preferred_days, preferred_start_time, preferred_end_time, same_day, note = line.strip().split(',')
            parts = line.strip().split(',')
            instructor_name = parts[0]
            preferred_days = parts[1]
            preferred_start_time = parts[2]
            preferred_end_time = parts[3]
            same_day = parts[4]
            note = ','.join(parts[5:])
            course = {
                'instructor_name': instructor_name,
                'preferred_days': preferred_days,
                'preferred_start_time': preferred_start_time,
                'preferred_end_time': preferred_end_time,
                'same_day': same_day,
                'note': note
            }
            course_info.append(course)
    return course_info

course_data_file_path = 'examples/CoursesThisQuarter.csv'
course_info_file_path = 'examples/CourseInfo.csv'
instructor_info = 'examples/InstructorPref.csv'
courses_this_quarter_list = read_courses_this_quarter(course_data_file_path)
course_info_list = read_course_information(course_info_file_path)
instructor_info_list = read_instructor_information(instructor_info)

print('hello')

class Instructor:
    def __init__(self, instructor_name, preferred_days, preferred_start_time, preferred_end_time, same_day, note):
        self.instructor_name = instructor_name
        self.preferred_days = preferred_days
        self.preferred_start_time = preferred_start_time
        self.preferred_end_time = preferred_end_time
        self.same_day = same_day
        self.note = note

class Course:
    def __init__(self, name, instructor, days, start_time, end_time, note):
        self.name = name
        self.instructor = instructor
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.note = note

class CourseInfo:
    def __init__(self, name, session_length, num_sessions_per_week, is_large_class, ten_percent_rule_exempted_class, ten_percent_rule_exempted_TA, mustOnDays, start_time, end_time):
        self.name = name
        self.session_length = session_length
        self.num_sessions_per_week = num_sessions_per_week
        self.is_large_class = is_large_class
        self.ten_percent_rule_exempted_class = ten_percent_rule_exempted_class
        self.ten_percent_rule_exempted_TA = ten_percent_rule_exempted_TA
        self.mustOnDays = mustOnDays
        self.start_time = start_time
        self.end_time = end_time

# DATA STRUCTURE
# loop through the courses and create a list of course objects
courses_this_quarter = []
for course in courses_this_quarter_list:
    courses_this_quarter.append(Course(course['course_name'], course['instructor_name'], course['days'], course['start_time'], course['end_time'], course['note']))

# DATA STRUCTURE
# loop through the course info and create a list of course info objects
course_information = []
for course in course_info_list:
    course_information.append(CourseInfo(course['course_name'], course['session_length'], course['num_sessions_per_week'], course['is_large_class'], course['10_percent_rule_exempted_class'], course['10_percent_rule_exempted_TA'], course['mustOnDays'], course['start_time'], course['end_time']))

# DATA STRUCTURE
# loop through the instructor info and create a list of instructor objects
instructor_preferences = []
for instructor in instructor_info_list:
    instructor_preferences.append(Instructor(instructor['instructor_name'], instructor['preferred_days'], instructor['preferred_start_time'], instructor['preferred_end_time'], instructor['same_day'], instructor['note']))

# DATA STRUCTURE
# list of (day, time) where day = M-F and time is 8:00-6:00 in 30 minute increments
time_slots = []
days = ['M', 'T', 'W', 'H', 'F']
for day in days:
    for hour in range(8, 18):  # 8:00 to 17:00
        for minute in [0, 30]:
            start_time = f"{hour:02d}:{minute:02d}"
            # end_hour = hour if minute == 0 else hour + 1
            # end_minute = 30 if minute == 0 else 0
            # end_time = f"{end_hour:02d}:{end_minute:02d}"
            time_slots.append((day, start_time))


#print(time_slots)
#print('hello')

from pulp import *

# # Create variables and parameters as dictionaries
# instructor_vars = pulp.LpVariable.dicts(
#     "instructor", (instructor.instructor_name for instructor in instructor_preferences)

# courses_this_quarter_vars = pulp.LpVariable.dicts(
#     "course", (course.name for course in courses_this_quarter))

# # Create the 'course_schedule' variable to specify
# course_information_vars = pulp.LpVariable.dicts(
#     "course_info", (course.name for course in course_information)
# )

# define the problem
prob = LpProblem("HW4", LpMaximize)

# define decision variables
x = pulp.LpVariable.dicts('course_', ((course.name, t) for course in courses_this_quarter for t in time_slots), cat='Binary')    # x_c,t

# additional decision variables

# Objective function is first
#prob += pulp.LpMaximize()

prob += pulp.lpSum(x[course.name, t] for course in courses_this_quarter for t in time_slots)

# Constraints
# Each course must be scheduled exactly once
# for course in courses_this_quarter:
#     prob += pulp.lpSum(x[course.name, t] for t in time_slots) == 1

# determine the length of each class and the number of sessions per week
for course in course_information:
    prob += pulp.lpSum(x[course.session_length, t] for t in time_slots) == course.session_length

# constraints for ##-minute classes
for course in course_information:
    if course.length == 50:
        allowed_start_times = [8.5, 9.5, 10.5, 11.5, 12.5, 13.5]  # Represented in hours
        for time_slot in time_slots:
            if time_slot not in allowed_start_times:
                prob += x[course.name, time_slot] == 0
    if course.length == 80:
        allowed_start_times = [8.5, 10, 11.5, 13]
        for time_slot in time_slots:
            if time_slot not in allowed_start_times:
                prob += x[course.name, time_slot] == 0
    if course.length == 110:
        allowed_start_times = [8.5, 10.5, 12.5, 13.5]
        for time_slot in time_slots:
            if time_slot not in allowed_start_times:
                prob += x[course.name, time_slot] == 0





# solve
prob.solve()

# print the optimal solution
for course in courses_this_quarter:
    for t in time_slots:
        if pulp.value(x[course.name, t]) == 1:
            print(f"Course {course.name} is scheduled at time slot {t}")