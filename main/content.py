"""Default site content. Used to seed the database and as a fallback so pages are never empty."""

SERVICES = [
    ('Manpower Recruitment', 'Blue-collar and white-collar recruitment for every industry, sourced from many countries and placed with employers in the UAE, the wider Gulf, Europe and beyond.', 'fa-users'),
    ('Tourism', 'Professional tourism services and travel arrangements for business and leisure.', 'fa-plane-departure'),
    ('Trade', 'Facilitating international trade and business development from our Dubai headquarters to Africa, the Middle East and the rest of the world.', 'fa-handshake'),
    ('Consultation', 'HR strategy, workforce planning and talent management advice from experienced consultants.', 'fa-lightbulb'),
    ('Training', 'Customised skills, technical and soft-skills training that prepares workers for overseas employment.', 'fa-chalkboard-teacher'),
    ('Airline Ticketing', 'Competitive airline ticketing and reservations, including group bookings, with 24/7 support.', 'fa-ticket-alt'),
]

SERVICE_POINTS = {
    'Manpower Recruitment': ['Blue-collar workers', 'White-collar professionals', 'Skilled technicians', 'Management staff'],
    'Tourism': ['Travel planning', 'Tour packages', 'Business travel', 'Visa assistance'],
    'Trade': ['Trade facilitation', 'Business networking', 'Market access', 'Partnership development'],
    'Consultation': ['HR strategy development', 'Workforce planning', 'Talent management', 'Process optimisation'],
    'Training': ['Skills development', 'Technical training', 'Soft skills coaching', 'Certification programmes'],
    'Airline Ticketing': ['Flight bookings', 'Competitive pricing', 'Group bookings', '24/7 support'],
}

RECRUITMENT_FIELDS = [
    ('Administrative Fields', 'Top-tier talent for administrative positions including executive secretaries, managers and skilled professionals.', 'fa-user-tie', ['Executive secretaries', 'Office managers', 'Receptionists', 'Data & records staff']),
    ('Engineering & Construction', 'Professionals across civil, electrical, mechanical, chemical engineering, IT, architecture and safety.', 'fa-hard-hat', ['Civil engineering', 'Architecture', 'Electrical & mechanical', 'Safety & technical fields']),
    ('Medical & Paramedical', 'Health workers across all specialties, male and female.', 'fa-heartbeat', ['Doctors', 'Nurses', 'Caregivers', 'Paramedics', 'Home care specialists']),
    ('Security Guards', 'Highly trained security personnel for offices, commercial establishments and residential properties.', 'fa-shield-alt', ['Security guards', 'Security officers', 'Supervisors', 'Security managers']),
    ('Professional Drivers', 'Professional, dedicated and reliable drivers ensuring comfort and safety.', 'fa-car', ['Personal drivers', 'Chauffeurs', 'Corporate drivers', 'Heavy vehicle operators']),
    ('Hospitality & Tourism', 'Chefs, baristas, airline crew, waitstaff, housekeepers, bartenders and flight personnel.', 'fa-hotel', ['Chefs & baristas', 'Waitstaff & stewards', 'Housekeepers & bartenders', 'Cabin crew']),
    ('Education', 'Educators across science, languages, computer science, English, law and mathematics.', 'fa-graduation-cap', ['Science teachers', 'Language instructors', 'Computer science', 'English, law & maths']),
    ('Marketing Fields', 'Salespersons, sales executives, cashiers and shop managers.', 'fa-chart-line', ['Salespersons', 'Sales executives', 'Cashiers', 'Shop managers']),
    ('Tailoring & Beauty', 'Specialists in tailoring, design, embroidery, hairdressing, makeup and cosmetics.', 'fa-cut', ['Tailoring', 'Embroidery & design', 'Hairdressing', 'Makeup & cosmetics']),
]

CORE_VALUES = ['ACCOUNTABILITY', 'INTEGRITY', 'QUALITY', 'HUMBLENESS AND WILLPOWER', 'PROFESSIONALISM',
               'FOCUS ON IMPACT', 'CELEBRATE SUCCESS', 'RESPONSIBILITY', 'TRUST', 'PASSION']

OFFICES = [
    ('Dubai, UAE', 'GLOBIS HR CONSULTANCY FZE LLC', 'Office# 510, Mai Tower, Al Nahda, Dubai, UAE', True),
    ('Nigeria', 'SERAH RECRUITMENT & SERVICES', 'Lagos, Nigeria', False),
    ('Ghana', 'GLOBIS RECRUITMENT AGENCY LTD.', 'Accra, Ghana', False),
    ('Uganda', 'GLOBIS HR SOLUTIONS UGANDA LTD.', 'Kampala, Uganda', False),
    ('Kenya', 'GLOBIS HR CONSULTANCY LTD.', 'Mombasa, Kenya', False),
    ('Uganda – Mbale', 'GLOBIS HR SOLUTIONS UGANDA LTD. (Mbale branch)', 'Mbale, Uganda', False),
]

# (title, category, city, type, salary, vacancies, summary, description, requirements, benefits, featured)
JOBS = [
    ('Security Guard', 'security', 'Dubai', 'full_time', 'AED 1,500 – 2,000 / month', 50,
     'Guards for malls, offices and residential towers across Dubai.',
     'Protect people and property at commercial and residential sites. You will patrol, monitor access, write short shift reports and respond calmly to incidents.',
     'Age 21 – 40\nPhysically fit, good character\nBasic English or Arabic\nPrevious security experience is an advantage\nValid passport',
     'Accommodation\nTransport to site\nEmployment visa\nMedical insurance\nAir ticket', True),
    ('Professional Driver', 'driving', 'Dubai', 'full_time', 'AED 1,800 – 2,500 / month', 30,
     'Light-vehicle and chauffeur drivers for corporate and private clients.',
     'Safe, punctual driving for executives, families and company fleets across the UAE.',
     'Clean driving record, 2+ years experience\nUAE licence or a licence that can be converted\nGood knowledge of road safety\nBasic English\nValid passport',
     'Accommodation\nEmployment visa\nMedical insurance\nAir ticket\nOvertime pay', True),
    ('Construction Labourer', 'construction', 'Abu Dhabi', 'contract', 'AED 1,200 – 1,600 / month', 120,
     'General labourers for large building and infrastructure projects.',
     'Site preparation, material handling, assisting skilled trades and keeping sites safe and tidy.',
     'Age 20 – 45\nPhysically fit\nWillingness to work outdoors\nPrevious site experience preferred\nValid passport',
     'Accommodation\nFood allowance\nTransport\nEmployment visa\nMedical insurance', False),
    ('Hotel Housekeeper', 'hospitality', 'Dubai', 'full_time', 'AED 1,400 – 1,900 / month', 25,
     'Housekeeping staff for 4 and 5-star hotels and serviced apartments.',
     'Clean and prepare guest rooms and public areas to hotel standards.',
     'Previous housekeeping experience preferred\nAttention to detail\nBasic English\nTeam player\nValid passport',
     'Accommodation\nUniform\nMeals on duty\nEmployment visa\nMedical insurance', False),
    ('Waiter / Waitress', 'hospitality', 'Dubai', 'full_time', 'AED 1,500 – 2,200 / month + tips', 20,
     'Front-of-house team for restaurants, cafés and hotels.',
     'Welcome guests, take orders, serve food and drinks and keep a friendly, professional service standard.',
     'Good spoken English\nCustomer service attitude\nPrevious restaurant experience is an advantage\nValid passport',
     'Accommodation\nUniform\nTips\nEmployment visa\nMedical insurance', False),
    ('Cleaner / Facilities Staff', 'cleaning', 'Sharjah', 'full_time', 'AED 1,100 – 1,500 / month', 60,
     'Cleaners for offices, malls, schools and residential buildings.',
     'Daily cleaning and upkeep of buildings in line with company standards.',
     'No experience required, training provided\nReliable and hard-working\nValid passport',
     'Accommodation\nTransport\nEmployment visa\nMedical insurance', False),
    ('Registered Nurse', 'medical', 'Dubai', 'full_time', 'AED 4,000 – 7,000 / month', 10,
     'Nurses for hospitals, clinics and home-care providers.',
     'Provide patient care, administer treatment and keep accurate clinical records.',
     'Nursing diploma or degree\nValid nursing licence\n2+ years experience\nGood English\nValid passport',
     'Accommodation\nEmployment visa\nMedical insurance\nAir ticket\nAnnual leave', False),
    ('Sales Executive / Cashier', 'sales', 'Dubai', 'full_time', 'AED 1,800 – 3,000 / month', 15,
     'Retail sales and cashier roles in supermarkets and fashion stores.',
     'Serve customers, handle payments, merchandise shelves and support daily store targets.',
     'Good English, Arabic is a plus\nCustomer-focused\nBasic computer skills\nValid passport',
     'Accommodation\nEmployment visa\nMedical insurance\nSales commission', False),
]
