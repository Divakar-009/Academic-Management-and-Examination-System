from django.urls import path
from .views import *
from rest_framework import routers 


router=routers.DefaultRouter()
router.register(r"payroll/pending", PendingPaymentListView, basename="pending-payroll")
router.register(r"payroll/paid", HRSalaryTeacherList, basename="paid-payrolls")


urlpatterns =router.urls+ [
    path("payroll/<int:pk>/",TeachersSalaryDetailView.as_view()),
    path("paySalary/<int:payroll_id>/pay/",PayTeacherSalaryApi.as_view()),
    path("status/<int:payment_id>/",PaymentStatusApi.as_view()),
    path("status/sendMail/<int:payment_id>/",SendMail.as_view()),
    path("salary_Confirm/<int:payment_id>/",PaymentreciptApiView.as_view()),
    path("webhooks/paypal/", paypal_webhook, name="paypal_webhook"),
    path("payroll/paidDetail/<int:teacher_id>/", HRTeacherSalaryDetail.as_view()),
    path("teacher/paidDetail/<int:teacher_id>/", TeacherSalaryDetail.as_view()),
]