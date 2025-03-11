from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.list import ListView
import csv
from django.db.models.functions import TruncYear, TruncMonth
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Income
from expenses.models import Expense


@login_required(login_url="login")
def dashboard(request):
    expense = Expense.objects.filter(owner=request.user).aggregate(Sum("amount"))
    income = Income.objects.filter(user=request.user).aggregate(Sum("amount"))

    if expense["amount__sum"] is None:
        # type: ignore
        expense["amount__sum"] = "0"
    else:
        expense["amount__sum"]

    if income["amount__sum"] is None:
        # type: ignore
        income["amount__sum"] = "0"
    else:
        income["amount__sum"]

    totalbalance = float(income["amount__sum"]) - float(expense["amount__sum"])
    if totalbalance is None:
        # type: ignore
        totalbalance = "0"
    else:
        totalbalance = totalbalance

    expenses_by_category = (
        Expense.objects.filter(owner=request.user)
        .values("category_expense__title")  # Группировка по названию категории
        .annotate(total=Sum("amount"))
        .order_by("-total")  # Сортируем по убыванию суммы
    )

    # Преобразуем данные в JSON-совместимый формат
    expenses_data_category = list(expenses_by_category)
    print(expenses_data_category)
    # Группируем и суммируем расходы по году и месяцу
    expenses = (
        Expense.objects.filter(owner=request.user)
        .annotate(year=TruncYear("date"), month=TruncMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("amount"))
        .order_by("year", "month")
    )

    # Группируем и суммируем доходы по году и месяцу
    incomes = (
        Income.objects.filter(user=request.user)
        .annotate(year=TruncYear("date"), month=TruncMonth("date"))
        .values("year", "month")
        .annotate(total=Sum("amount"))
        .order_by("year", "month")
    )

    # Преобразуем данные в удобный JSON-формат
    expenses_data = [
        {"year": exp["year"].year, "month": exp["month"].month, "total": exp["total"]}
        for exp in expenses
    ]

    incomes_data = [
        {"year": inc["year"].year, "month": inc["month"].month, "total": inc["total"]}
        for inc in incomes
    ]

    context = {
        "expenses_data": expenses_data,
        "incomes_data": incomes_data,
        "expenses_data_category" : expenses_data_category,
        "totolIncome": income["amount__sum"],
        "totalExpense": expense["amount__sum"],
        "total_balance": totalbalance,
    }
    print("EXPENSES:", expenses_data)
    print("INCOMES:", incomes_data)
    return render(request, "index.html", context)


class IncomeList(LoginRequiredMixin, ListView):
    model = Income
    template_name = "income/income.html"
    context_object_name = "incomes"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["incomes"] = Income.objects.filter(user=self.request.user)
        return context


class CreateIncome(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Income
    fields = ["amount", "description", "sources", "category"]
    success_url = reverse_lazy("income")
    template_name = "income/addIncome.html"
    success_message = "Income successfully created"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateIncome, self).form_valid(form)


class UpdateIncome(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Income
    fields = ["amount", "description", "sources"]
    success_url = reverse_lazy("income")
    success_message = "Income successfully updated"


class deleteINcome(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Income
    context_object_name = "incomes"
    success_url = reverse_lazy("income")
    success_message = "Income successfully deleted"

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

@login_required(login_url="login")
def exportIncome(request):
    response = HttpResponse(content_type="text/csv")

    w = csv.writer(response)
    w.writerow(["Amount", "Description",  "Sources", "Time and Date"])

    for income in Income.objects.filter(user=request.user).values_list(
       "amount", "description", "sources", "date"
    ):
        w.writerow(income)

    response["Content-Disposition"] = "attachment; filename=Income_summary.csv"
    return response
