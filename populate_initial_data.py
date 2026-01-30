"""
Script to populate initial data for AnimalType and ServiceType models.
Run this with: python manage.py shell < populate_initial_data.py
Or copy and paste into Django shell
"""

from apps.users.models import AnimalType, ServiceType

# Create Animal Types
animal_types = [
    'dog',
    'cat',
    'bird',
    'rabbit',
    'chicken',
    'hamster',
    'other',
]

for animal_type in animal_types:
    obj, created = AnimalType.objects.get_or_create(animal_type=animal_type)
    if created:
        print(f'Created AnimalType: {obj.get_animal_type_display()}')
    else:
        print(f'AnimalType already exists: {obj.get_animal_type_display()}')

# Create Service Types
service_types = [
    'keepsitter',
    'keephost',
    'keepwalk',
]

for service_type in service_types:
    obj, created = ServiceType.objects.get_or_create(service_type=service_type)
    if created:
        print(f'Created ServiceType: {obj.get_service_type_display()}')
    else:
        print(f'ServiceType already exists: {obj.get_service_type_display()}')

print('\n✅ Initial data populated successfully!')
