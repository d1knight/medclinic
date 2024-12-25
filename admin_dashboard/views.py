from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, Service, Visit
from django.core.paginator import Paginator
from django.contrib import messages


def show_dashboard(request):
    return render(request,'admin_dashboard/main.html')


def patient_list(request):
    patient = Patient.objects.all()
    paginator = Paginator(patient, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'admin_dashboard/patient_list.html', {'page_obj':page_obj})

def service_list(request):
    service = Service.objects.all()
    paginator = Paginator(service, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'admin_dashboard/service_list.html', {'page_obj':page_obj})




def visit_add(request):
    patients = Patient.objects.all()
    services = Service.objects.all()

    if request.method == 'POST':
        # Получение данных из формы
        patient_id = request.POST.get('patient')
        service_ids = request.POST.getlist('services')  # Список ID выбранных услуг

        # Проверка существования пациента
        patient = get_object_or_404(Patient, id=patient_id)

        # Создание визита
        visit = Visit.objects.create(patient=patient)  # Создание и сохранение объекта Visit

        # Проверка, что ID был присвоен
        if not visit.id:
            raise ValueError("Объект Visit не был сохранён корректно.")

        # Установка связи ManyToMany
        visit.services.set(service_ids)
        visit.save()  # Пересчёт суммы и финальное сохранение

        return redirect('admin_dashboard:visit_list')  # Перенаправление на список визитов

    return render(request, 'admin_dashboard/visit_add.html', {'patients': patients, 'services': services})




def visit_list(request):
    search_query = request.GET.get('q', '')  # Фильтр по имени пациента
    sort_by = request.GET.get('sort', '-id')  # Сортировка (по умолчанию: новейшие визиты)

    # Фильтруем визиты по имени пациента
    visits = Visit.objects.filter(patient__first_name__icontains=search_query)

    # Сортируем визиты
    visits = visits.order_by(sort_by)

    paginator = Paginator(visits, 4)  # Пагинация (4 визита на странице)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'admin_dashboard/visit_list.html', context)


def visit_print(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    template = loader.get_template('admin_dashboard/visit_print.html')
    context = {'visit': visit}
    html = template.render(context)

    # Временная заглушка: выводим HTML как PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="visit_{visit.id}.pdf"'
    response.write(html.encode('utf-8'))  # PDF-генерация будет добавлена позже
    return response


def visit_payment(request, visit_id):
    visit = Visit.objects.get(id=visit_id)

    # Проверяем, если визит уже оплачен, перенаправляем обратно с сообщением
    if visit.payment_status == 'paid':
        return redirect('admin_dashboard:visit_list')  # Или перенаправьте на другую страницу

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        paid_amount = float(request.POST.get('paid_amount', 0))

        # Добавляем оплаченную сумму к общей
        visit.paid_amount += paid_amount
        visit.remaining_amount = visit.total_price - visit.paid_amount

        # Проверяем, если оставшаяся сумма 0, обновляем статус на 'paid'
        if visit.remaining_amount <= 0:
            visit.payment_status = 'paid'

        # Сохраняем изменения
        visit.save()

        return redirect('admin_dashboard:visit_list')  # Перенаправляем на список визитов

    return render(request, 'admin_dashboard/visit_payment.html', {'visit': visit})


def patient_add(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        adress = request.POST.get('adress')
        telephone = request.POST.get('telephone')

        # Создание нового пациента
        Patient.objects.create(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            adress=adress,
            telephone=telephone
        )

        return redirect('admin_dashboard:patient_list')

    return render(request, 'admin_dashboard/patient_add.html')


def service_add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')

        # Создание нового пациента
        Service.objects.create(
            name=name,
            price=price,
        )

        return redirect('admin_dashboard:service_list')

    return render(request, 'admin_dashboard/service_add.html')


def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == "POST":
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.birth_date = request.POST.get('birth_date')
        patient.gender = request.POST.get('gender')
        patient.adress = request.POST.get('adress')
        patient.telephone = request.POST.get('telephone')
        
        # Здесь слаг будет автоматически обновлен благодаря сигналу
        patient.save()

        return redirect('admin_dashboard:patient_list')
    
    return render(request, 'admin_dashboard/patient_edit.html', {'patient': patient})


def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == "POST":
        service.name = request.POST.get('name')
        service.price = request.POST.get('price')
        
        service.save()

        return redirect('admin_dashboard:service_list')
    
    return render(request, 'admin_dashboard/service_edit.html', {'service': service})



def delete_patient(request,patient_id):
    patient = get_object_or_404(Patient,id=patient_id)
    if request.method == 'POST':
        patient.delete()
        return redirect('admin_dashboard:patient_list')
    return render(request,'admin_dashboard/patient_delete.html',{'patient':patient})


def delete_service(request,service_id):
    service = get_object_or_404(Service,id=service_id)
    if request.method == 'POST':
        service.delete()
        return redirect('admin_dashboard:service_list')
    return render(request,'admin_dashboard/service_delete.html',{'service':service})