from django.core.management.base import BaseCommand

from main import content
from main.models import CoreValue, Job, Office, RecruitmentField, Service


class Command(BaseCommand):
    help = 'Seed default site content. Safe to run repeatedly: never deletes or overwrites admin edits.'

    def handle(self, *args, **opts):
        n = 0
        for i, (title, desc, icon) in enumerate(content.SERVICES, 1):
            _, c = Service.objects.get_or_create(title=title, defaults={'description': desc, 'icon': icon, 'order': i})
            n += c
        for i, (title, desc, icon, _pts) in enumerate(content.RECRUITMENT_FIELDS, 1):
            _, c = RecruitmentField.objects.get_or_create(title=title, defaults={'description': desc, 'icon': icon, 'order': i})
            n += c
        for i, title in enumerate(content.CORE_VALUES, 1):
            _, c = CoreValue.objects.get_or_create(number=i, defaults={'title': title})
            n += c
        for i, (country, company, address, main) in enumerate(content.OFFICES, 1):
            _, c = Office.objects.get_or_create(company_name=company, defaults={
                'country': country, 'address': address, 'is_main': main, 'order': i})
            n += c
        # Demo jobs only when explicitly requested (SEED_SAMPLE_JOBS=1) — real jobs are added in the portal
        import os
        if os.environ.get('SEED_SAMPLE_JOBS') == '1' and not Job.objects.exists():
            for (title, cat, city, typ, salary, vac, summary, desc, req, ben, feat) in content.JOBS:
                Job.objects.create(title=title, category=cat, city=city, employment_type=typ, salary=salary,
                                   vacancies=vac, summary=summary, description=desc, requirements=req,
                                   benefits=ben, is_featured=feat)
                n += 1
        self.stdout.write(self.style.SUCCESS(f'Seed complete ({n} new records).'))
