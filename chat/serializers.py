from rest_framework import serializers
from .models import *

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender_name",
            "is_sender",
            "content",
            "timestamp"
        ]

class GroupRoomSerializer(serializers.ModelSerializer):
    last_message=serializers.SerializerMethodField()
    class Meta:
        model=Group_Room
        fields=['id','name','last_message']
    def get_last_message(self,obj):
        last_msg=obj.mssg.order_by('-timestamp').first()
        if last_msg:
            return{
                "content":last_msg.content,
                "timestamp":last_msg.timestamp,
                "sender":last_msg.sender
            }
        return None
    
class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group_message
        fields = [
            "id",
            "sender",
            "is_sender",
            "content",
            "timestamp"
        ]

class GroupMemberViewSerializer(serializers.ModelSerializer):
    memberInfo = serializers.SerializerMethodField()
    class Meta:
        model = Group_Room
        fields = ['id', 'name', 'memberInfo']
    def get_memberInfo(self, obj):
        data = []
        for member in obj.group_members.all():
            if member.user_type == "STUDENT":
                data.append({
                    "id": member.student.id,
                    "name": member.student.name,
                    "role": member.role,
                    "user_type": "student",
                    "joined_at": member.joined_at
                })
            elif member.user_type == "TEACHER":
                data.append({
                    "id": member.teacher.id,
                    "name": member.teacher.name,
                    "role": member.role,
                    "user_type": "teacher",
                    "joined_at": member.joined_at
                })
        return data
