# Campus data with real universities
CAMPUS_DATA = [
    {"name": "University of Illinois at Urbana-Champaign", "city": "Champaign", "state": "IL", "code": "UIUC"},
    {"name": "Northwestern University", "city": "Evanston", "state": "IL", "code": "NU"},
    {"name": "University of Chicago", "city": "Chicago", "state": "IL", "code": "UC"},
    {"name": "DePaul University", "city": "Chicago", "state": "IL", "code": "DPU"},
    {"name": "Stanford University", "city": "Stanford", "state": "CA", "code": "STAN"},
    {"name": "MIT", "city": "Cambridge", "state": "MA", "code": "MIT"},
    {"name": "Harvard University", "city": "Cambridge", "state": "MA", "code": "HARV"},
    {"name": "UC Berkeley", "city": "Berkeley", "state": "CA", "code": "UCB"},
]

# Dining halls by campus
DINING_DATA = {
    "UIUC": ["Ikenberry Dining Center", "Lincoln Avenue Dining Hall", "Pennsylvania Avenue Dining Hall", "Busey-Evans Food Court", "57 North"],
    "NU": ["Allison Dining Hall", "Elder Dining Hall", "Sargent Dining Hall", "Plex West", "Norris Food Court"],
    "UC": ["Bartlett Dining Commons", "Baker Dining Commons", "Cathey Dining Commons", "South Campus Dining Hall"],
    "DPU": ["Student Center Dining", "Brownstone's Café", "Daley Building Food Court", "Loop Campus Dining"],
    "STAN": ["Stern Dining", "Wilbur Dining", "FloMo Café", "Lakeside Dining", "Arrillaga Family Dining Commons"],
    "MIT": ["Maseeh Dining", "Next House Dining", "Simmons Hall Dining", "Student Center Food Court"],
    "HARV": ["Annenberg Hall", "Adams House Dining", "Winthrop House Dining", "Leverett House Dining"],
    "UCB": ["Crossroads", "Foothill Dining", "Café 3", "Clark Kerr Campus Dining"]
}

# Study locations by campus
STUDY_DATA = {
    "UIUC": ["Main Library", "Undergraduate Library", "Engineering Library", "Grainger Library", "Study Room A101", "Union Study Lounge"],
    "NU": ["Main Library", "Mudd Science Library", "Deering Library", "Tech Study Rooms", "Norris Study Spaces"],
    "UC": ["Regenstein Library", "Crerar Library", "Mansueto Library", "Study Pods Level 2", "Harper Memorial Library"],
    "DPU": ["Richardson Library", "Loop Campus Library", "Study Commons", "Quiet Study Rooms", "Group Study Areas"],
    "STAN": ["Green Library", "Engineering Library", "Meyer Library", "Study Rooms Building 160", "24/7 Study Spaces"],
    "MIT": ["Hayden Library", "Rotch Library", "Study Rooms E25", "Stata Center Study", "Student Center Study"],
    "HARV": ["Widener Library", "Lamont Library", "Cabot Science Library", "Study Rooms Leverett", "24/7 Study Spaces"],
    "UCB": ["Doe Library", "Moffitt Library", "Engineering Library", "Study Rooms MLK", "24/7 Study Spaces"]
}

# Major categories
MAJORS_DATA = [
    {"name": "Computer Science", "department": "Engineering", "degree_type": "BS"},
    {"name": "Electrical Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Mechanical Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Civil Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Business Administration", "department": "Business", "degree_type": "BS"},
    {"name": "Economics", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Psychology", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Biology", "department": "Sciences", "degree_type": "BS"},
    {"name": "Chemistry", "department": "Sciences", "degree_type": "BS"},
    {"name": "Physics", "department": "Sciences", "degree_type": "BS"},
    {"name": "Mathematics", "department": "Sciences", "degree_type": "BS"},
    {"name": "Statistics", "department": "Sciences", "degree_type": "BS"},
    {"name": "English Literature", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "History", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Political Science", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "International Relations", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Pre-Med", "department": "Sciences", "degree_type": "Track"},
    {"name": "Pre-Law", "department": "Liberal Arts", "degree_type": "Track"},
]

# Course data by department
COURSES_DATA = {
    "Computer Science": [
        ("CS101", "Introduction to Computer Science", "Easy"),
        ("CS225", "Data Structures", "Medium"),
        ("CS233", "Computer Architecture", "Medium"),
        ("CS374", "Algorithms and Models of Computation", "Hard"),
        ("CS411", "Database Systems", "Medium"),
        ("CS440", "Artificial Intelligence", "Hard"),
        ("CS498", "Machine Learning", "Hard")
    ],
    "Mathematics": [
        ("MATH221", "Calculus I", "Medium"),
        ("MATH231", "Calculus II", "Medium"),
        ("MATH241", "Calculus III", "Hard"),
        ("MATH415", "Linear Algebra", "Medium"),
        ("MATH461", "Probability Theory", "Hard"),
        ("MATH464", "Statistical Theory", "Hard")
    ],
    "Physics": [
        ("PHYS211", "University Physics: Mechanics", "Medium"),
        ("PHYS212", "University Physics: Elec & Mag", "Medium"),
        ("PHYS213", "University Physics: Thermal Physics", "Hard"),
        ("PHYS435", "Electromagnetic Fields", "Hard")
    ],
    "Chemistry": [
        ("CHEM102", "General Chemistry I", "Medium"),
        ("CHEM104", "General Chemistry II", "Medium"),
        ("CHEM232", "Organic Chemistry I", "Hard"),
        ("CHEM233", "Organic Chemistry II", "Hard")
    ],
    "Business": [
        ("BUS101", "Introduction to Business", "Easy"),
        ("BUS200", "Financial Accounting", "Medium"),
        ("BUS300", "Corporate Finance", "Hard"),
        ("BUS400", "Strategic Management", "Hard")
    ],
    "Biology": [
        ("BIO101", "General Biology", "Easy"),
        ("BIO201", "Cell Biology", "Medium"),
        ("BIO301", "Genetics", "Hard"),
        ("BIO401", "Molecular Biology", "Hard")
    ]
}

# Demo user names for realistic matches
DEMO_NAMES = [
    "Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emily Davis", "James Wilson",
    "Jessica Garcia", "David Kim", "Amanda Miller", "Ryan Thompson", "Lauren Brown",
    "Kevin Lee", "Sophia Martinez", "Tyler Anderson", "Maya Patel", "Jordan White",
    "Chloe Taylor", "Nathan Moore", "Zoe Jackson", "Ethan Harris", "Grace Liu",
    "Brandon Clark", "Olivia Lewis", "Austin Walker", "Isabella Hall", "Logan Young"
]