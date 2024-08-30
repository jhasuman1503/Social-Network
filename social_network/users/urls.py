from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserSignupView,
    UserLoginView,
    UserSearchView,
    FriendRequestView,
    FriendRequestActionView,
    ListFriendsView,
    ListPendingRequestsView,
    ThrottledFriendRequestView
)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('friend-request/', ThrottledFriendRequestView.as_view(), name='friend_request'),
    path('friend-request/action/', FriendRequestActionView.as_view(), name='friend_request_action'),
    path('friends/', ListFriendsView.as_view(), name='list_friends'),
    path('pending-requests/', ListPendingRequestsView.as_view(), name='list_pending_requests'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
