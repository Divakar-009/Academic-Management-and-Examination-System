from django.urls import include, path
from . import views



urlpatterns = [
    path("chat/<int:room_id>/", views.chat_room, name="chat_room"),
    path("api/create-room/<int:student_id>/",views.CreateRoomView.as_view()),
    path("api/fetch-messages_teacher/<int:room_id>/", views.FetchMessagesTeacherPanelView.as_view()),
    path("api/fetch-messages_student/<int:room_id>/", views.FetchMessagesStudentPanelView.as_view()),
    path("api/CreateTeacherMessage/<int:room_id>/", views.TeacherSendMessageView.as_view()),
    path("api/CreateStudentMessage/<int:room_id>/", views.StudentSendMessageView.as_view()),

    path("api/CreateGroup/", views.CreateGroupRoomView.as_view()),
    path("api/addMemberbyteacher/<int:room_id>/", views.AddGroupMembersbyTeacherView.as_view()),
    path("api/addMemberbystudent/<int:room_id>/", views.AddGroupMembersbyStudentView.as_view()),
    path("api/makeGroupAdminbyTeacher/<int:room_id>/", views.ManageGroupAdminsByTeacherView.as_view()),
    path("api/makeGroupAdminbyStudent/<int:room_id>/", views.ManageGroupAdminsByStudentView.as_view()),
    path("api/viewGroupmemeber_teacher/<int:room_id>/", views.ViewGroupMembersbyTeacherApi.as_view()),
    path("api/viewGroupmemeber_student/<int:room_id>/", views.ViewGroupMembersbyStudentApi.as_view()),
    path("api/removeGroupmemeber_teacher/<int:room_id>/", views.MemberRemovefromGroupByTeacher.as_view()),
    path("api/removeGroupmemeber_student/<int:room_id>/", views.MemberRemovefromGroupByStudent.as_view()),
    path("api/GroupsListbyTeacher/", views.TeacherGroupRoomListView.as_view()),
    path("api/GroupsListbyStudent/", views.StudentGroupRoomListView.as_view()),
    path("api/SendTeacherMsgGroup/<int:room_id>/", views.TeacherSendMessageInGroupChatView.as_view()),
    path("api/SendStudentMsgGroup/<int:room_id>/", views.StudentSendMessageInGroupChatView.as_view()),
    path("api/fetch-groupMessages_teacher/<int:room_id>/", views.FetchGroupMessagesTeacherPanelView.as_view()),
    path("api/fetch-groupMessages_student/<int:room_id>/", views.FetchGroupMessagesStudentPanelView.as_view()),

]