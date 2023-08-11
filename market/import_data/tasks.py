from __future__ import absolute_import, unicode_literals
import os
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from config.celery import app
from import_data.services import process_product
from products.models import Import


@app.task
def import_products(file_path, email):  # noqa F401
    """функция/task для импорта данных"""
    try:
        products, errors = process_product(file_path)
    except (ValueError, FileNotFoundError, PermissionError, IOError, KeyError) as error:
        return "Завершён с ошибкой", [str(error)]

    if app.control.inspect().active():
        return "Завершён с ошибкой", ["Предыдущий импорт ещё не выполнен. Пожалуйста, дождитесь его окончания"]

    if errors:
        os.rename(file_path, os.path.join(settings.IMPORT_FAIL, os.path.basename(file_path)))
    else:
        os.rename(file_path, os.path.join(settings.IMPORT_DONE, os.path.basename(file_path)))

    subject = "Результат импорта товаров"
    message = f'Импорт товаров из файла {file_path} был {"успешно" if not errors else "неуспешно"} выполнен.\n'
    if errors:
        message += "В ходе импорта возникли следующие ошибки:\n"
        for error in errors:
            message += f"- {error}\n"
    message += "Спасибо за использование нашего сервиса."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
    import_obj = Import.objects.get(source=file_path)
    import_obj.status = "running"
    import_obj.start_time = timezone.now()
    import_obj.end_time = None  # Инициализируем значение end_time
    import_obj.imported_count = None  # Инициализируем значение imported_count
    import_obj.save()
    try:
        import_obj.status = "completed"
        import_obj.end_time = timezone.now()
        import_obj.imported_count = len(products)
        import_obj.save()
        return f"Импорт из {file_path} успешно завершен. Импортировано {len(products)} товаров."
    except (ValueError, PermissionError, IOError, KeyError) as e:
        import_obj.status = "failed"
        import_obj.end_time = timezone.now()
        import_obj.errors.append(str(e))
        import_obj.save()
        return f"Импорт из {file_path} завершен с ошибкой. Ошибка: {e}"
