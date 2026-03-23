from rest_framework import serializers

from payment_app.models import *
from teacher_app.models import TecherRegist


class miniTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=TecherRegist
        fields=['id','name','email']

class teacherSalarySerializer(serializers.ModelSerializer):
    teacher=miniTeacherSerializer(read_only=True)
    class Meta:
        model=Payroll
        fields= ["id","teacher","period_start","period_end","present_days"
                 ,"half_days","paid_leaves","lwp_days","gross_salary","deductions","net_salary","status","created_at"]



class payrollMiniSerializer(serializers.ModelSerializer):
    teacher=miniTeacherSerializer(read_only=True)
    class Meta:
        model=Payroll
        fields=['id','teacher','period_start','period_end']

class PaymentItemSerializer(serializers.ModelSerializer):
    payroll=payrollMiniSerializer(read_only=True)
    paypal_url = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields =[
            'id', 
            'payroll', 
            'paypal_batch_id', 
            'paypal_transction_id', 
            'amount', 
            'status',
            'paypal_url',
            'paid_at'
        ]
        read_only_fields = ['paypal_batch_id', 'paypal_transction_id', 'paid_at']
    def get_paypal_url(self,obj):
        if obj.paypal_transction_id:
            return f"https://www.paypal.com/activity/payment/{obj.paypal_transction_id}"
        return None
    



class PaidPaymentDetailSerializer(serializers.ModelSerializer):
    payroll=teacherSalarySerializer(read_only=True)
    paypal_url = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields =[
            'id', 
            'payroll', 
            'paypal_batch_id', 
            'paypal_transction_id',
            'paypal_url',
            'paid_at'
        ]
        read_only_fields = ['paypal_batch_id', 'paypal_transction_id', 'paid_at']
    def get_paypal_url(self,obj):
        if obj.paypal_transction_id:
            return f"https://www.paypal.com/activity/payment/{obj.paypal_transction_id}"
        return None
    
class teacherSalarySerializer(serializers.ModelSerializer):
    payment=PaymentItemSerializer(read_only=True)
    class Meta:
        model=Payroll
        fields= ["present_days"
                 ,"half_days","paid_leaves","lwp_days","gross_salary","deductions","net_salary","status","created_at","Payment"]
