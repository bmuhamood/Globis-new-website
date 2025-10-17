from django.core.management.base import BaseCommand
from main.models import Service, RecruitmentField, CoreValue, Office

class Command(BaseCommand):
    help = 'Load initial data for GLOBIS HR Consultancy'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Service.objects.all().delete()
        RecruitmentField.objects.all().delete()
        CoreValue.objects.all().delete()
        Office.objects.all().delete()

        # Create Services
        services_data = [
            {
                'title': 'Manpower Recruitment',
                'description': 'Expert recruitment services for blue-collar and white-collar personnel across all industries.',
                'icon': 'fa-users',
                'order': 1
            },
            {
                'title': 'Tourism',
                'description': 'Professional tourism services and travel arrangements for business and leisure.',
                'icon': 'fa-plane-departure',
                'order': 2
            },
            {
                'title': 'Trade',
                'description': 'Facilitating international trade and business development opportunities.',
                'icon': 'fa-handshake',
                'order': 3
            },
            {
                'title': 'Consultation',
                'description': 'Expert consultation services for HR strategy and workforce planning.',
                'icon': 'fa-lightbulb',
                'order': 4
            },
            {
                'title': 'Training',
                'description': 'Professional training programs to enhance workforce skills and capabilities.',
                'icon': 'fa-chalkboard-teacher',
                'order': 5
            },
            {
                'title': 'Airline Ticketing',
                'description': 'Convenient airline ticketing and reservation services worldwide.',
                'icon': 'fa-ticket-alt',
                'order': 6
            },
        ]

        for service_data in services_data:
            Service.objects.create(**service_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(services_data)} services'))

        # Create Recruitment Fields
        recruitment_data = [
            {
                'title': 'Administrative Fields',
                'description': 'Top-tier talent for administrative positions including executive secretaries, managers, and skilled professionals.',
                'icon': 'fa-user-tie',
                'order': 1
            },
            {
                'title': 'Engineering & Construction',
                'description': 'Professionals across civil, electrical, mechanical, chemical engineering, IT, architecture, and safety.',
                'icon': 'fa-hard-hat',
                'order': 2
            },
            {
                'title': 'Medical & Paramedical',
                'description': 'Health workers including doctors, nurses, caregivers, paramedics, and home care specialists.',
                'icon': 'fa-heartbeat',
                'order': 3
            },
            {
                'title': 'Security Guards',
                'description': 'Highly trained security personnel including guards, managers, officers, and supervisors.',
                'icon': 'fa-shield-alt',
                'order': 4
            },
            {
                'title': 'Professional Drivers',
                'description': 'Professional, dedicated, and reliable drivers ensuring comfort and safety.',
                'icon': 'fa-car',
                'order': 5
            },
            {
                'title': 'Hospitality & Tourism',
                'description': 'Chefs, baristas, airline crew, waitstaff, housekeepers, bartenders, and flight personnel.',
                'icon': 'fa-hotel',
                'order': 6
            },
            {
                'title': 'Education',
                'description': 'Educators across science, languages, computer science, English, law, and mathematics.',
                'icon': 'fa-graduation-cap',
                'order': 7
            },
            {
                'title': 'Marketing Fields',
                'description': 'Salespersons, sales executives, cashiers, and shop managers.',
                'icon': 'fa-chart-line',
                'order': 8
            },
            {
                'title': 'Tailoring & Beauty',
                'description': 'Specialists in tailoring, design, embroidery, hairdressing, makeup, and cosmetics.',
                'icon': 'fa-cut',
                'order': 9
            },
        ]

        for field_data in recruitment_data:
            RecruitmentField.objects.create(**field_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(recruitment_data)} recruitment fields'))

        # Create Core Values
        core_values_data = [
            {'number': 1, 'title': 'ACCOUNTABILITY'},
            {'number': 2, 'title': 'INTEGRITY'},
            {'number': 3, 'title': 'QUALITY'},
            {'number': 4, 'title': 'HUMBLENESS AND WILLPOWER'},
            {'number': 5, 'title': 'PROFESSIONALISM'},
            {'number': 6, 'title': 'FOCUS ON IMPACT'},
            {'number': 7, 'title': 'CELEBRATE SUCCESS'},
            {'number': 8, 'title': 'RESPONSIBILITY'},
            {'number': 9, 'title': 'TRUST'},
            {'number': 10, 'title': 'PASSION'},
        ]

        for value_data in core_values_data:
            CoreValue.objects.create(**value_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(core_values_data)} core values'))

        # Create Offices
        offices_data = [
            {
                'country': 'Dubai, UAE',
                'company_name': 'GLOBIS HR CONSULTANCY FZE LLC',
                'address': 'Office# 510, Mai Tower, Al Nahda, Dubai, UAE',
                'is_main': True,
                'order': 1
            },
            {
                'country': 'Nigeria',
                'company_name': 'SERAH RECRUITMENT & SERVICES',
                'address': 'Lagos, Nigeria',
                'is_main': False,
                'order': 2
            },
            {
                'country': 'Ghana',
                'company_name': 'GLOBIS RECRUITMENT AGENCY LTD.',
                'address': 'Accra, Ghana',
                'is_main': False,
                'order': 3
            },
            {
                'country': 'Uganda',
                'company_name': 'GLOBIS HR SOLUTIONS UGANDA LTD.',
                'address': 'Kampala, Uganda',
                'is_main': False,
                'order': 4
            },
            {
                'country': 'Kenya',
                'company_name': 'GLOBIS HR CONSULTANCY LTD.',
                'address': 'Mombasa, Kenya',
                'is_main': False,
                'order': 5
            },
        ]

        for office_data in offices_data:
            Office.objects.create(**office_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(offices_data)} offices'))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all initial data!'))