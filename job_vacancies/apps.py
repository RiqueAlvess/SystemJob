from django.apps import AppConfig


class JobVacanciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_vacancies'
    verbose_name = 'Vagas e Compliance PCD'

    def ready(self):
        pass