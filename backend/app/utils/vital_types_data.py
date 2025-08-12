"""
Hardcoded vital types data for the application.
This provides default vital types that can be used to seed the database
or return as static data for the GraphQL queries.
"""

VITAL_TYPES_DATA = [
    {
        'type_id': 1,
        'label': 'Blood Pressure',
        'unit': 'mmHg',
        'threshold': {
            'systolic': {'low': 90, 'high': 140},
            'diastolic': {'low': 60, 'high': 90}
        }
    },
    {
        'type_id': 2,
        'label': 'Heart Rate',
        'unit': 'bpm',
        'threshold': {'low': 60, 'high': 100}
    },
    {
        'type_id': 3,
        'label': 'Body Temperature',
        'unit': '°F',
        'threshold': {'low': 97.0, 'high': 99.5}
    },
    {
        'type_id': 4,
        'label': 'Blood Sugar',
        'unit': 'mg/dL',
        'threshold': {'low': 70, 'high': 140}
    },
    {
        'type_id': 5,
        'label': 'Weight',
        'unit': 'kg',
        'threshold': None  # Weight thresholds vary by individual
    },
    {
        'type_id': 6,
        'label': 'Oxygen Saturation',
        'unit': '%',
        'threshold': {'low': 95, 'high': None}  # Only low threshold matters
    },
    {
        'type_id': 7,
        'label': 'BMI',
        'unit': 'kg/m²',
        'threshold': {'low': 18.5, 'high': 25.0}
    },
    {
        'type_id': 8,
        'label': 'Cholesterol',
        'unit': 'mg/dL',
        'threshold': {'low': None, 'high': 200}
    }
]

def get_vital_types():
    """Return all vital types data."""
    return VITAL_TYPES_DATA

def get_vital_type_by_id(type_id):
    """Get a specific vital type by ID."""
    return next((vt for vt in VITAL_TYPES_DATA if vt['type_id'] == type_id), None)

def get_vital_type_by_label(label):
    """Get a specific vital type by label."""
    return next((vt for vt in VITAL_TYPES_DATA if vt['label'].lower() == label.lower()), None)
