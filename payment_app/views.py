from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from payment_app.serializers import *
from teacher_app.permisions import IsJWTAuthorized
from .models import Payment, Payroll, WebHookEvent
from .tasks import process_salary_payment, send_salary_receipt_email
import json
from django.db.models import Max
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,status


class PendingPaymentListView(viewsets.ModelViewSet):
    http_method_names=["get"]
    # permission_classes=[IsJWTAuthorized]
    serializer_class=teacherSalarySerializer
    queryset = Payroll.objects.select_related("teacher").all()
    def get_queryset(self):
        return self.queryset.filter(status="PENDING").order_by("created_at")
    

class TeachersSalaryDetailView(APIView):
    # permission_classes=[IsJWTAuthorized]
    def get(self,request,pk):
        payroll=Payroll.objects.filter(teacher=pk,status="PENDING").first()
        serializer=teacherSalarySerializer(payroll)
        return Response(serializer.data)


class PayTeacherSalaryApi(APIView):
    # permission_classes=[IsJWTAuthorized]
    def post(self,request, payroll_id):
        payroll = get_object_or_404(Payroll,id=payroll_id)
        if Payment.objects.filter(payroll=payroll, status="SUCCESS").exists():
            return Response({
                "error": "Salary already paid for this payroll"
            })
        existing_payment = Payment.objects.filter(payroll=payroll,status__in=["PENDING","PROCESSING"]).first()
        if existing_payment:
            return Response({
                "error":"Payment already in progress"
            })
        payment = Payment.objects.create(
            payroll=payroll,
            amount=payroll.net_salary,
            status="PENDING"
        )
    
        process_salary_payment.delay(payment.id)
        return Response({"message": "Payment processing started","payment_id": payment.id},status=status.HTTP_200_OK)


class PaymentStatusApi(APIView):
    def get(self,request,payment_id):
        payment=get_object_or_404(Payment,id=payment_id)
        return Response({
            "payment_id": payment.id,
            "status": payment.status
        })
    

class SendMail(APIView):
    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        if payment.status != "SUCCESS":
            return Response({
                "payment_id": payment.id,
                "status": payment.status,
                "message": "Payment not successful. Email not sent."
            }, status=400)
        payroll = payment.payroll
        teacher = payroll.teacher
        send_salary_receipt_email.delay(teacher.id, payroll.id)
        return Response({
            "payment_id": payment.id,
            "status": payment.status,
            "message": "Email sent successfully"
        })

@api_view(["POST"])
def paypal_webhook(request):
    try:
        payload = request.data
        event_id = payload.get("id")
        event_type = payload.get("event_type")
        resource = payload.get("resource", {})
        payout_transaction_id = resource.get("transaction_id")
        sender_item_id = resource.get("payout_item", {}).get("sender_item_id")
        if not sender_item_id:
            return Response({"status": "invalid_payload"})
        sender_item_id = int(sender_item_id)
        payment = Payment.objects.filter(id=sender_item_id).first()
        if not payment:
            return Response({"status": "payment_not_found"})
    except Exception as e:
        print("Webhook error:", e)
        return Response({"status": "error_handled"}, status=200)
    if WebHookEvent.objects.filter(event_id=event_id).exists():
        return Response({"status":"duplicate_event"})
    webHook_event=WebHookEvent.objects.create(
        event_id=event_id,
        event_type=event_type,
        payload=payload
    )
    if event_type == "PAYMENT.PAYOUTS-ITEM.SUCCEEDED":
        payment.status = "SUCCESS"
        payment.paypal_transction_id = payout_transaction_id
        payment.paid_at = timezone.now()
        payment.save()
        payroll = payment.payroll
        payroll.status = "PAID"
        payroll.save()
    elif event_type == "PAYMENT.PAYOUTS-ITEM.FAILED":
        payment.status = "FAILED"
        payment.save()
    return Response({"status": "ok"},status=status.HTTP_200_OK)



class PaymentreciptApiView(APIView):
    # permission_classes=[IsJWTAuthorized]
    def get(self,request,payment_id):
        try:
            payment=Payment.objects.get(id=payment_id)
            if payment.status!="SUCCESS":
                return Response({"error":"Payment details not yet available."},status=400)
            serializer=PaymentItemSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({"error":"Payment record not found"},status=404)


class HRSalaryTeacherList(viewsets.ModelViewSet):
    http_method_names=["get"]
    # permission_classes=[IsJWTAuthorized]
    serializer_class=teacherSalarySerializer
    queryset = Payroll.objects.select_related("teacher").all()
    def get_queryset(self):
        return self.queryset.filter(status="PAID").order_by("-created_at")
        
class HRTeacherSalaryDetail(APIView):
    # permission_classes=[IsJWTAuthorized]
    def get(self, request, teacher_id):
        payments = Payment.objects.filter(
            payroll__teacher_id=teacher_id,
            status="SUCCESS"
        ).select_related("payroll", "payroll__teacher").order_by("-paid_at")
        serializer = PaidPaymentDetailSerializer(payments, many=True)
        return Response(serializer.data)

class TeacherSalaryDetail(APIView):
    # permission_classes=[IsJWTAuthorized]
    def get(self, request, teacher_id):
        payments = Payment.objects.filter(
            payroll__teacher_id=teacher_id,
            status="SUCCESS"
        ).select_related(
            "payroll"
        ).order_by("-paid_at")
        serializer = PaidPaymentDetailSerializer(payments, many=True)
        return Response(serializer.data)
        

    



    