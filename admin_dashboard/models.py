from django.utils import timezone  # Correct import
from django.db import models
from django.core.exceptions import ValidationError

import re

def validate_date_format(value):
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', value):
        raise ValidationError('Дата должна быть в формате DD-MM-YYYY.')

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Мужской'), ('F', 'Женский')])
    address = models.CharField(max_length=255,default='')
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

<<<<<<< HEAD
class Speciality(models.Model):
    name = models.CharField(max_length=100)
=======



class Visit(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    services = models.ManyToManyField('Service')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.JSONField()

    # Добавляем поле payment_status
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
    ]
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
    )

    def calculate_total_price(self):
        """
        Рассчитываем итоговую стоимость на основе связанных услуг.
        """
        return sum(service.price for service in self.services.all())

    def save(self, *args, **kwargs):
        """
        Переопределённый метод save:
        - Сохраняем объект без расчёта total_price для избежания проблем с ManyToMany.
        - После сохранения объекта и установки связей, обновляем total_price.
        - Обновляем статус оплаты.
        """
        is_new = self.pk is None  # Проверяем, новый ли это объект
        super().save(*args, **kwargs)  # Сохраняем объект

        # После сохранения (и только для существующих объектов) пересчитываем total_price
        if not is_new:
            self.total_price = self.calculate_total_price()
            self.remaining_amount = self.total_price - self.paid_amount

            # Обновляем статус оплаты
            if self.remaining_amount <= 0:
                self.payment_status = 'paid'
            else:
                self.payment_status = 'pending'
            
            super().save(update_fields=['total_price', 'remaining_amount', 'payment_status'])  # Сохраняем только изменённые поля
>>>>>>> c57154d27fe01d8dac89a2b16848664be7283ab9

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Payment(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Visit(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='visits'  # Добавляем related_name
    )
    services = models.ManyToManyField(Service)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20,
        choices=[('not_paid', 'Не оплачен'), ('partially_paid', 'Частично оплачен'), ('paid', 'Оплачен')],
        default='not_paid'
    )
    visit_date = models.DateField(default=timezone.now, null=True, blank=True)
    reason = models.TextField(blank=True)

    def update_payment_status(self):
        """Обновляет статус оплаты на основе суммы"""
        if self.paid_amount >= self.total_price:
            self.payment_status = 'paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'not_paid'
        self.save()

    def __str__(self):
        return f"Визит {self.patient.first_name} {self.patient.last_name}"


