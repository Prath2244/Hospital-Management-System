import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Doctor

def create_doctors():
    specialties = [
        'Cardiologist', 'Dermatologist', 'Emergency', 
        'Neurologist', 'Pediatrician', 'Psychiatrist'
    ]
    
    doctors_data = [
        ('Cardiologist', 'John', 'Smith', 'Jane', 'Doe'),
        ('Dermatologist', 'James', 'Johnson', 'Mary', 'Williams'),
        ('Emergency', 'Robert', 'Brown', 'Patricia', 'Jones'),
        ('Neurologist', 'Michael', 'Garcia', 'Jennifer', 'Miller'),
        ('Pediatrician', 'William', 'Davis', 'Linda', 'Martinez'),
        ('Psychiatrist', 'David', 'Rodriguez', 'Barbara', 'Hernandez'),
    ]
    
    created_count = 0
    for specialty, m_first, m_last, f_first, f_last in doctors_data:
        male_username = f"{m_first.lower()}.{m_last.lower()}"
        if not User.objects.filter(username=male_username).exists():
            user = User.objects.create_user(
                username=male_username,
                password='password123',
                first_name=m_first,
                last_name=m_last
            )
            Doctor.objects.create(
                user=user,
                mobile=f"+1 555-{100 + created_count:03d}-{100 + created_count:04d}",
                department=specialty,
                address=f"123 Male St, City {created_count+1}",
                status=True
            )
            print(f"✅ Created Male {specialty}: {m_first} {m_last}")
            created_count += 1
        else:
            print(f"⏩ Skipped {m_first} {m_last} (already exists)")
        
        female_username = f"{f_first.lower()}.{f_last.lower()}"
        if not User.objects.filter(username=female_username).exists():
            user = User.objects.create_user(
                username=female_username,
                password='password123',
                first_name=f_first,
                last_name=f_last
            )
            Doctor.objects.create(
                user=user,
                mobile=f"+1 555-{200 + created_count:03d}-{200 + created_count:04d}",
                department=specialty,
                address=f"456 Female Ave, City {created_count+1}",
                status=True
            )
            print(f"✅ Created Female {specialty}: {f_first} {f_last}")
            created_count += 1
        else:
            print(f"⏩ Skipped {f_first} {f_last} (already exists)")
    
    print(f"\n🎉 Successfully created/verified {created_count} doctors!")

if __name__ == '__main__':
    create_doctors()