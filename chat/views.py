from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.db import transaction
from django.db.models import Max
from rest_framework.exceptions import *
from chat.pagination import ChatPagination
from chat.serializers import *
from student_app.permissions import IsStudent
from teacher_app.models import *
from student_app.models import *
from django.conf import settings
from chat.models import *
from student_app.models import Student
from teacher_app.models import TecherRegist
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from teacher_app.permisions import IsJWTAuthorized
from django.db.models.functions import Coalesce

def chat_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    print("hey what is problem",room_id)
    context = {
        "room_id": room_id,
        "user_id": request.user.id,
        "user_type": "teacher" if hasattr(request.user, 'teacher') else "student"
    }
    return render(request, "chat.html", context)

class CreateRoomView(APIView):
    permission_classes=[IsJWTAuthorized]

    def post(self,request,student_id):
        student=get_object_or_404(Student,id=student_id)

        room,created=Room.objects.get_or_create(
            teacher=request.user,student=student        
            )
        
        if created:
            return Response(
        {"room_id": room.id, "created": True},
        status=status.HTTP_201_CREATED
    )
        else:
            return Response(
        {"room_id": room.id, "created": False},
        status=status.HTTP_200_OK
    )


# class FetchMessagesTeacherPanelView(APIView):
#     permission_classes=[IsJWTAuthorized]
#     def get(self,request,room_id):
#         user=request.user
#         try:
#             room=Room.objects.get(id=room_id)
#         except Room.DoesNotExist:
#             return Response({"error":"Room not Found"},status=status.HTTP_404_NOT_FOUND)
#         if request.user != room.teacher:
#             return Response({"error": "Not allowed"}, status=403)
#         messages=Message.objects.filter(room=room)
#         serializer=MessageSerializer(messages,many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class FetchMessagesTeacherPanelView(ListAPIView):
    serializer_class=MessageSerializer
    pagination_class=ChatPagination
    permission_classes=[IsJWTAuthorized]
    def get_queryset(self):
        user=self.request.user
        room_id=self.kwargs['room_id']
        room=get_object_or_404(Room,id=room_id,teacher=user)

        return room.messages.all().order_by("-timestamp")

class FetchMessagesStudentPanelView(ListAPIView):
    permission_classes=[IsStudent]
    serializer_class=MessageSerializer
    pagination_class=ChatPagination
    def get_queryset(self):
        user=self.request.user
        room_id=self.kwargs['room_id']
        room=get_object_or_404(Room,id=room_id,student=user)

        return Message.objects.filter(room=room).order_by("-timestamp")

    
class TeacherSendMessageView(APIView):
    permission_classes = [IsJWTAuthorized]

    def post(self, request,room_id):
        teacher = request.user
        content = request.data.get("content")

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        message = Message.objects.create(
            room=room,
            sender_name=teacher.name,
            is_sender=True,
            content=content

        )

        return Response({
            "message_id": message.id,
            "sender_name":message.sender_name,
            "is_sender":message.is_sender,
            "content": message.content
        }, status=201)
    
class StudentSendMessageView(APIView):
    permission_classes = [IsStudent]
    def post(self, request,room_id):
        student=request.user
        content = request.data.get("content")

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        message = Message.objects.create(
            room=room,
            sender_name=student.name,
            is_sender=True,
            content=content
        )

        return Response({
            "message_id": message.id,
            "sender_name":message.sender_name,
            "is_sender":message.is_sender,
            "content": message.content
        }, status=201)
    

####################################################
##   APIs for Group Chat between Teacher-students ##
####################################################

class CreateGroupRoomView(APIView):
    permission_classes = [IsJWTAuthorized]

    def post(self, request):
        owner = request.user
        room_name = request.data.get("room_name")

        room = Group_Room.objects.create(
            name=room_name,
            owner=owner
        )
        if isinstance(owner, TecherRegist):
            GroupMember.objects.create(
                group=room,
                teacher=owner,
                user_type="TEACHER",
                role="ADMIN"
            )

        elif isinstance(owner, Student):
            GroupMember.objects.create(
                group=room,
                student=owner,
                user_type="STUDENT",
                role="ADMIN"
            )

        return Response({
            "message": "Group created successfully",
            "room_id": room.id
        }, status=201)
    

class AddGroupMembersbyStudentView(APIView):
    permission_classes = [IsStudent]
    def post(self, request, room_id):
        user = request.user
        room = get_object_or_404(Group_Room, id=room_id)
        is_admin = GroupMember.objects.filter(
            group=room,
            student=user,
            role="ADMIN"
        ).exists()
        if not is_admin:
            return Response({"message": "Only admins can manage members"}, status=403)
        student_ids = request.data.get("student_id", [])
        teacher_ids = request.data.get("teacher_id", [])
        added_members = []
        with transaction.atomic():
            if student_ids:
                students = Student.objects.filter(id__in=student_ids)
                student_members = [
                    GroupMember(
                    group=room,
                    student=student,
                    user_type="STUDENT",
                    role="MEMBER"
                )
                for student in students
            ]
                GroupMember.objects.bulk_create(student_members,ignore_conflicts=True)
            added_members.extend([f"Student {s.id}" for s in students])
            if teacher_ids:
                teachers = TecherRegist.objects.filter(id__in=teacher_ids)
                teacher_members = [
                GroupMember(
                    group=room,
                    teacher=teacher,
                    user_type="TEACHER",
                    role="MEMBER"
                )
                for teacher in teachers
                ]
                GroupMember.objects.bulk_create(
                    teacher_members,
                    ignore_conflicts=True
                )
            added_members.extend([f"Teacher {t.id}" for t in teachers])
        return Response({
            "message": "Members processed successfully",
            "attempted_to_add": added_members
        }, status=200)

class AddGroupMembersbyTeacherView(APIView):
    permission_classes = [IsJWTAuthorized]
    def post(self, request, room_id):
        user = request.user
        room = get_object_or_404(Group_Room, id=room_id)
        is_admin = GroupMember.objects.filter(
            group=room,
            teacher=user,
            role="ADMIN"
        ).exists()
        if not is_admin:
            return Response({"message": "Only admins can manage members"}, status=403)
        student_ids = request.data.get("student_id", [])
        teacher_ids = request.data.get("teacher_id", [])
        added_members = []
        with transaction.atomic():
            if student_ids:
                students = Student.objects.filter(id__in=student_ids)
                student_members = [GroupMember(group=room,
                    student=student,
                    user_type="STUDENT",
                    role="MEMBER")
                    for student in students
            ]
                GroupMember.objects.bulk_create(
                    student_members,
                    ignore_conflicts=True  
            )
            added_members.extend([f"Student {s.id}" for s in students])
            if teacher_ids:
                teachers = TecherRegist.objects.filter(id__in=teacher_ids)
                teacher_members = [
                    GroupMember(
                        group=room,
                        teacher=teacher,
                        user_type="TEACHER",
                        role="MEMBER"
                    )
                    for teacher in teachers
                ]
                GroupMember.objects.bulk_create(
                    teacher_members,
                    ignore_conflicts=True
                    )
            added_members.extend([f"Teacher {t.id}" for t in teachers])
        return Response({
            "message": "Members processed successfully",
            "attempted_to_add": added_members
        }, status=200)





class MemberRemovefromGroupByTeacher(APIView):
    permission_classes=[IsJWTAuthorized]
    def post(self,request,room_id):
        user=request.user
        room=get_object_or_404(Group_Room,id=room_id)
        is_admin=GroupMember.objects.filter(group=room,teacher=user,role="ADMIN").exists()
        if not is_admin:
            return Response({"message": "Only admins can manage members"}, status=403)
        student_ids=request.data.get("student_id",[])
        teacher_ids=request.data.get("teacher_id",[])
        admin_count = GroupMember.objects.filter(group=room,role="ADMIN").count()
        if admin_count == 1:
            return Response({"message": "Cannot remove last admin"}, status=400)
        removed=[]
        if student_ids:
            GroupMember.objects.filter(
                group=room,
                student_id__in=student_ids
            ).delete()
            removed.extend([f"student {sid}" for sid in student_ids])
        if teacher_ids:
            GroupMember.objects.filter(
                group=room,
                teacher_id__in=teacher_ids
            ).delete()
            removed.extend({f"teacher {tid}" for tid in teacher_ids})
        return Response({
            "message": "Members removed successfully",
            "removed_members": removed
        }, status=200)

class MemberRemovefromGroupByStudent(APIView):
    permission_classes=[IsStudent]
    def post(self,request,room_id):
        user=request.user
        room=get_object_or_404(Group_Room,id=room_id)
        is_admin=GroupMember.objects.filter(group=room,student=user,role="ADMIN").exists()
        if not is_admin:
            return Response({"message": "Only admins can manage members"}, status=403)
        student_ids=request.data.get("student_id",[])
        teacher_ids=request.data.get("teacher_id",[])
        admin_count = GroupMember.objects.filter(group=room,role="ADMIN").count()
        if admin_count == 1:
            return Response({"message": "Cannot remove last admin"}, status=400)
        removed=[]
        if student_ids:
            GroupMember.objects.filter(
                group=room,
                student_id__in=student_ids
            ).delete()
            removed.extend([f"student {sid}" for sid in student_ids])
        if teacher_ids:
            GroupMember.objects.filter(
                group=room,
                teacher_id__in=teacher_ids
            ).delete()
            removed.extend({f"teacher {tid}" for tid in teacher_ids})
        return Response({
            "message": "Members removed successfully",
            "removed_members": removed
        }, status=200)






class ManageGroupAdminsByTeacherView(APIView):
    permission_classes = [IsJWTAuthorized]
    def post(self, request, room_id):
        user = request.user
        room = get_object_or_404(Group_Room, id=room_id)
        is_admin = GroupMember.objects.filter(
            group=room,
            teacher=user,
            role="ADMIN"
        ).exists()
        if not is_admin:
            return Response({"message": "Only admins can manage admins"}, status=403)
        student_ids = request.data.get("student_id", [])
        teacher_ids = request.data.get("teacher_id", [])
        GroupMember.objects.filter(
            group=room,
            student_id__in=student_ids
        ).update(role="ADMIN")
        GroupMember.objects.filter(
            group=room,
            teacher_id__in=teacher_ids
        ).update(role="ADMIN")
        return Response({"message": "Admins updated successfully"}, status=200)

class ManageGroupAdminsByStudentView(APIView):
    permission_classes=[IsStudent]
    def post(self, request, room_id):
        user = request.user
        room = get_object_or_404(Group_Room, id=room_id)
        is_admin = GroupMember.objects.filter(
            group=room,
            student=user,
            role="ADMIN"
        ).exists()
        if not is_admin:
            return Response({"message": "Only admins can manage admins"}, status=403)
        student_ids = request.data.get("student_id", [])
        teacher_ids = request.data.get("teacher_id", [])
        GroupMember.objects.filter(
            group=room,
            student_id__in=student_ids
        ).update(role="ADMIN")
        GroupMember.objects.filter(
            group=room,
            teacher_id__in=teacher_ids
        ).update(role="ADMIN")
        return Response({"message": "Admins updated successfully"}, status=200)




class ViewGroupMembersbyTeacherApi(ListAPIView):
    permission_classes=[IsJWTAuthorized]
    def get(self,request,room_id):
        group=get_object_or_404(Group_Room,id=room_id)
        serializer=GroupMemberViewSerializer(group)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ViewGroupMembersbyStudentApi(APIView):
    permission_classes=[IsStudent]
    def get(self,request,room_id):
        group=get_object_or_404(Group_Room,id=room_id)
        serializer=GroupMemberViewSerializer(group)
        return Response(serializer.data,status=status.HTTP_200_OK)




class TeacherGroupRoomListView(ListAPIView):
    serializer_class=GroupRoomSerializer
    permission_classes=[IsJWTAuthorized]

    def get_queryset(self):
        user=self.request.user

        rooms=Group_Room.objects.filter(group_members__teacher=user)

        return rooms.annotate(
            last_message_at=Coalesce(Max('mssg__timestamp'),'created_at')
        ).order_by('-last_message_at')
    
class StudentGroupRoomListView(ListAPIView):
    serializer_class=GroupRoomSerializer
    permission_classes=[IsStudent]

    def get_queryset(self):
        user=self.request.user

        rooms=Group_Room.objects.filter(group_members__student=user)

        return rooms.annotate(
            last_message_at=Coalesce(Max('mssg__timestamp'),'created_at')
        ).order_by('-last_message_at')




class TeacherSendMessageInGroupChatView(APIView):
    permission_classes = [IsJWTAuthorized]
    def post(self, request, room_id):
        teacher = request.user
        content = request.data.get("content")
        room = get_object_or_404(Group_Room, id=room_id)
        is_member = GroupMember.objects.filter(
            group=room,
            teacher=teacher
        ).exists()
        if not is_member:
            return Response({"error": "Not a group member"}, status=403)
        message = Group_message.objects.create(
            room=room,
            sender=teacher.name,
            content=content,
            is_sender=True
        )
        return Response({
            "message_id": message.id,
            "sender": message.sender,
            "content": message.content,
            "timestamp": message.timestamp
        }, status=201)

class StudentSendMessageInGroupChatView(APIView):
    permission_classes = [IsStudent]
    def post(self, request, room_id):
        student = request.user
        content = request.data.get("content")
        room = get_object_or_404(Group_Room, id=room_id)
        is_member = GroupMember.objects.filter(
            group=room,
            student=student
        ).exists()
        if not is_member:
            return Response({"error": "Not a group member"}, status=403)
        message = Group_message.objects.create(
            room=room,
            sender=student.name,
            content=content,
            is_sender=True
        )
        return Response({
            "message_id": message.id,
            "sender": message.sender,
            "content": message.content,
            "timestamp": message.timestamp
        }, status=201)




class FetchGroupMessagesTeacherPanelView(ListAPIView):
    serializer_class=GroupMessageSerializer
    pagination_class=ChatPagination
    permission_classes=[IsJWTAuthorized]
    def get_queryset(self):
        user=self.request.user
        room_id=self.kwargs['room_id']
        room=get_object_or_404(Group_Room,id=room_id,group_members__teacher=user)
        return room.mssg.all().order_by("-timestamp")

class FetchGroupMessagesStudentPanelView(ListAPIView):
    serializer_class=GroupMessageSerializer
    pagination_class=ChatPagination
    permission_classes=[IsStudent]
    def get_queryset(self):
        user=self.request.user
        room_id=self.kwargs['room_id']
        room=get_object_or_404(Group_Room,id=room_id,group_members__student=user)
        return room.mssg.all().order_by("-timestamp")
    
