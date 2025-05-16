from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.template import loader
from .models import Patient, Service, Visit
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings


def show_dashboard(request):
    return render(request, 'admin_dashboard/main.html')


def patient_list(request):
    patients = Patient.objects.all()
    paginator = Paginator(patients, 10)  # Пагинация по 10 записи
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_dashboard/patient_list.html', {'page_obj': page_obj})


def patient_add(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        address = request.POST.get('adress')
        telephone = request.POST.get('telephone')

        Patient.objects.create(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            telephone=telephone
        )
        return redirect('admin_dashboard:patient_list')

    return render(request, 'admin_dashboard/patient_add.html')


def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.birth_date = request.POST.get('birth_date')
        patient.gender = request.POST.get('gender')
        patient.address = request.POST.get('adress')
        patient.telephone = request.POST.get('telephone')
        patient.save()

        return redirect('admin_dashboard:patient_list')

    return render(request, 'admin_dashboard/patient_edit.html', {'patient': patient})


def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        patient.delete()
        return redirect('admin_dashboard:patient_list')

    return render(request, 'admin_dashboard/patient_delete.html', {'patient': patient})


def service_list(request):
    services = Service.objects.all()
    paginator = Paginator(services, 10)  # Пагинация по 10 записи
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_dashboard/service_list.html', {'page_obj': page_obj})


def service_add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')

        Service.objects.create(name=name, price=price)
        return redirect('admin_dashboard:service_list')

    return render(request, 'admin_dashboard/service_add.html')


def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        service.name = request.POST.get('name')
        service.price = request.POST.get('price')
        service.save()

        return redirect('admin_dashboard:service_list')

    return render(request, 'admin_dashboard/service_edit.html', {'service': service})


def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service.delete()
        return redirect('admin_dashboard:service_list')

    return render(request, 'admin_dashboard/service_delete.html', {'service': service})


def visit_list(request):
    search_query = request.GET.get('q', '')  # Фильтр по имени пациента
    sort_by = request.GET.get('sort', '-id')  # Сортировка (по умолчанию: новейшие визиты)

    visits = Visit.objects.filter(patient__first_name__icontains=search_query)
    visits = visits.order_by(sort_by)

    paginator = Paginator(visits, 10)  # Пагинация по 4 записи
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/visit_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    })


def visit_add(request):
    patients = Patient.objects.all()
    services = Service.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        service_ids = request.POST.getlist('services')
        reason = request.POST.get('reason')  # Получаем причину болезни
        patient = get_object_or_404(Patient, id=patient_id)

        visit = Visit.objects.create(
            patient=patient,
            reason=reason  # Сохраняем причину болезни
        )
        visit.services.set(service_ids)

        # Пересчет итоговой суммы
        total_price = sum(service.price for service in visit.services.all())
        visit.total_price = total_price
        visit.save()

        # Сообщение об успешном добавлении визита
        messages.success(request, f'Визит для пациента {patient.first_name} {patient.last_name} успешно добавлен.')

        return redirect('admin_dashboard:visit_list')

    return render(request, 'admin_dashboard/visit_add.html', {'patients': patients, 'services': services})


def visit_payment(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)

    # Если визит уже полностью оплачен, запретить дополнительную оплату
    if visit.payment_status == 'paid':  
        messages.info(request, "Этот визит уже полностью оплачен.")
        return redirect('admin_dashboard:visit_list')

    # Вычисляем оставшуюся сумму для оплаты
    remaining_amount = visit.total_price - visit.paid_amount

    if request.method == 'POST':
        # Получаем данные из формы
        payment_method = request.POST.get('payment_method')
        paid_amount = request.POST.get('paid_amount', 0)

        try:
            # Преобразуем сумму в Decimal
            paid_amount = Decimal(paid_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception as e:
            messages.error(request, "Введите корректную сумму.")
            return redirect('admin_dashboard:visit_payment', visit_id)

        # Проверяем, если цена визита была изменена
        remaining_amount = visit.total_price - visit.paid_amount
        if paid_amount > remaining_amount:
            messages.error(request, f"Введённая сумма ({paid_amount}) превышает требуемую ({remaining_amount}). Проверьте стоимость визита.")
            return redirect('admin_dashboard:visit_payment', visit_id)

        # Обновляем оплаченные суммы
        visit.paid_amount += paid_amount
        visit.paid_amount = visit.paid_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Обновляем статус оплаты
        if visit.paid_amount >= visit.total_price:
            visit.paid_amount = visit.total_price
            visit.payment_status = 'paid'  # Полностью оплачено
        elif visit.paid_amount > 0:
            visit.payment_status = 'partially_paid'  # Частично оплачено
        else:
            visit.payment_status = 'not_paid'  # Не оплачено

        # Сохраняем изменения в базе
        visit.save()

        messages.success(request, "Оплата успешно обновлена!")
        return redirect('admin_dashboard:visit_list')

    return render(request, 'admin_dashboard/visit_payment.html', {
        'visit': visit,
        'remaining_amount': remaining_amount
    })


def visit_print(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    
    # Путь к шрифту
    font_path = os.path.join(settings.BASE_DIR, 'admin_dashboard/static/fonts/FreeSerif.ttf')
    
    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont('FreeSerif', font_path))

    # Создаем HTTP-ответ с типом контента для PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="visit_{visit.id}.pdf"'

    # Создаем PDF с использованием ReportLab
    c = canvas.Canvas(response, pagesize=letter)

    # Устанавливаем шрифт
    c.setFont("FreeSerif", 12)

    # Информация о визите
    c.drawString(100, 750, f"ID Визита: {visit.id}")
    c.drawString(100, 730, f"Имя и фамилия пациента: {visit.patient.first_name} {visit.patient.last_name}")
    c.drawString(100, 710, f"Дата рождения: {visit.patient.birth_date}")
    c.drawString(100, 670, f"Адрес: {visit.patient.address}")
    c.drawString(100, 650, f"Телефон: {visit.patient.telephone}")
    
    # Информация о визите
    c.drawString(100, 630, f"Дата визита: {visit.visit_date}")
    c.drawString(100, 610, f"Итоговая сумма: {visit.total_price} Сум")
    c.drawString(100, 590, f"Выплаченная сумма: {visit.paid_amount} Сум")
    
    # Статус оплаты
    if visit.payment_status == 'paid':
        payment_status = 'Оплачен'
    elif visit.payment_status == 'partially_paid':
        payment_status = 'Частично оплачен'
    else:
        payment_status = 'Не оплачен'
    
    c.drawString(100, 570, f"Статус оплаты: {payment_status}")

    # Услуги
    services = visit.services.all()
    c.drawString(100, 550, "Предоставленные услуги:")
    y_position = 530
    for service in services:
        c.drawString(100, y_position, f"- {service.name}")
        y_position -= 20  # Сдвигаем строку вниз для следующей услуги
    
    # Завершаем создание PDF
    c.showPage()
    c.save()

    return response



def patient_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    visits = patient.visits.order_by('-visit_date')  # Доступ через related_name
    return render(request, 'admin_dashboard/patient_history.html', {
        'patient': patient,
        'visits': visits,
    })
