"""Countries with ISO code, name and international dialling code.
Recruitment source countries are listed first in PRIORITY order."""

# (iso2, name, dial_code)
_ALL = [
    ('UG', 'Uganda', '256'), ('KE', 'Kenya', '254'), ('NG', 'Nigeria', '234'), ('GH', 'Ghana', '233'),
    ('TZ', 'Tanzania', '255'), ('RW', 'Rwanda', '250'), ('ET', 'Ethiopia', '251'), ('ZM', 'Zambia', '260'),
    ('ZW', 'Zimbabwe', '263'), ('MW', 'Malawi', '265'), ('CM', 'Cameroon', '237'), ('SL', 'Sierra Leone', '232'),
    ('LR', 'Liberia', '231'), ('SN', 'Senegal', '221'), ('CI', "Côte d'Ivoire", '225'), ('BI', 'Burundi', '257'),
    ('SS', 'South Sudan', '211'), ('SD', 'Sudan', '249'), ('EG', 'Egypt', '20'), ('MA', 'Morocco', '212'),
    ('IN', 'India', '91'), ('PK', 'Pakistan', '92'), ('BD', 'Bangladesh', '880'), ('NP', 'Nepal', '977'),
    ('LK', 'Sri Lanka', '94'), ('PH', 'Philippines', '63'), ('ID', 'Indonesia', '62'),
    ('AE', 'United Arab Emirates', '971'),
    ('AF', 'Afghanistan', '93'), ('AL', 'Albania', '355'), ('DZ', 'Algeria', '213'), ('AO', 'Angola', '244'),
    ('AR', 'Argentina', '54'), ('AM', 'Armenia', '374'), ('AU', 'Australia', '61'), ('AT', 'Austria', '43'),
    ('AZ', 'Azerbaijan', '994'), ('BH', 'Bahrain', '973'), ('BY', 'Belarus', '375'), ('BE', 'Belgium', '32'),
    ('BJ', 'Benin', '229'), ('BW', 'Botswana', '267'), ('BR', 'Brazil', '55'), ('BF', 'Burkina Faso', '226'),
    ('KH', 'Cambodia', '855'), ('CA', 'Canada', '1'), ('CV', 'Cape Verde', '238'),
    ('CF', 'Central African Republic', '236'), ('TD', 'Chad', '235'), ('CN', 'China', '86'),
    ('CO', 'Colombia', '57'), ('KM', 'Comoros', '269'), ('CG', 'Congo', '242'),
    ('CD', 'DR Congo', '243'), ('DJ', 'Djibouti', '253'), ('ER', 'Eritrea', '291'), ('SZ', 'Eswatini', '268'),
    ('FR', 'France', '33'), ('GA', 'Gabon', '241'), ('GM', 'Gambia', '220'), ('GE', 'Georgia', '995'),
    ('DE', 'Germany', '49'), ('GN', 'Guinea', '224'), ('GW', 'Guinea-Bissau', '245'), ('HT', 'Haiti', '509'),
    ('IR', 'Iran', '98'), ('IQ', 'Iraq', '964'), ('IE', 'Ireland', '353'), ('IT', 'Italy', '39'),
    ('JP', 'Japan', '81'), ('JO', 'Jordan', '962'), ('KZ', 'Kazakhstan', '7'), ('KW', 'Kuwait', '965'),
    ('KG', 'Kyrgyzstan', '996'), ('LB', 'Lebanon', '961'), ('LS', 'Lesotho', '266'), ('LY', 'Libya', '218'),
    ('MG', 'Madagascar', '261'), ('MY', 'Malaysia', '60'), ('MV', 'Maldives', '960'), ('ML', 'Mali', '223'),
    ('MR', 'Mauritania', '222'), ('MU', 'Mauritius', '230'), ('MX', 'Mexico', '52'), ('MM', 'Myanmar', '95'),
    ('MZ', 'Mozambique', '258'), ('NA', 'Namibia', '264'), ('NL', 'Netherlands', '31'), ('NZ', 'New Zealand', '64'),
    ('NE', 'Niger', '227'), ('OM', 'Oman', '968'), ('PS', 'Palestine', '970'), ('PL', 'Poland', '48'),
    ('PT', 'Portugal', '351'), ('QA', 'Qatar', '974'), ('RO', 'Romania', '40'), ('RU', 'Russia', '7'),
    ('SA', 'Saudi Arabia', '966'), ('SC', 'Seychelles', '248'), ('SG', 'Singapore', '65'), ('SO', 'Somalia', '252'),
    ('ZA', 'South Africa', '27'), ('KR', 'South Korea', '82'), ('ES', 'Spain', '34'), ('SE', 'Sweden', '46'),
    ('CH', 'Switzerland', '41'), ('SY', 'Syria', '963'), ('TH', 'Thailand', '66'), ('TG', 'Togo', '228'),
    ('TN', 'Tunisia', '216'), ('TR', 'Türkiye', '90'), ('UA', 'Ukraine', '380'), ('GB', 'United Kingdom', '44'),
    ('US', 'United States', '1'), ('UZ', 'Uzbekistan', '998'), ('VN', 'Vietnam', '84'), ('YE', 'Yemen', '967'),
    ('ST', 'São Tomé and Príncipe', '239'), ('GQ', 'Equatorial Guinea', '240'),
]

COUNTRIES = [{'iso': i, 'name': n, 'dial': d} for i, n, d in _ALL]
BY_ISO = {c['iso']: c for c in COUNTRIES}

# Nationality list = every country name; priority ones first, remainder alphabetical.
_PRIORITY = 28  # first 28 entries are priority (UG ... AE)
NATIONALITY_CHOICES = (
    [(c['name'], c['name']) for c in COUNTRIES[:_PRIORITY - 1]]
    + [(c['name'], c['name']) for c in sorted(COUNTRIES[_PRIORITY - 1:], key=lambda c: c['name'])]
)
RESIDENCE_CHOICES = NATIONALITY_CHOICES
