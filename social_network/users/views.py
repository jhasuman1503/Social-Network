from django.shortcuts import render

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import CustomUser, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
import time
from django.core.cache import cache

class UserSignupView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists.')
        password = self.request.data.get('password')
        serializer.save(password=password)




class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        print(email,password)
        user = authenticate(request, email=email, password=password)

        if user is not None:

            login(request, user)

     
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'status': 'logged in',
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')


        user = authenticate(request, email=email, password=password)

        if user is not None:

            login(request, user)


            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'logged in',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        User = CustomUser

        try:
            user = User.objects.get(email=email)
            print(user)
            if user.password != password:
                return Response({'status': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                n=login(request, user)
                print(n)
                return Response({'status': 'logged in'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'status': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        

       


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        keyword = self.request.query_params.get('q', '').strip()  
        print('@' in keyword,keyword)
        if keyword:
            
            if '@' in keyword:
                return CustomUser.objects.filter(email__iexact=keyword)
            return CustomUser.objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
        return CustomUser.objects.none()  


class FriendRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get('to_user')
        to_user = CustomUser.objects.get(id=to_user_id)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'status': 'friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'status': 'friend request sent'}, status=status.HTTP_201_CREATED)


class FriendRequestActionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')  
        friend_request_id = request.data.get('friend_request_id')
        
        try:
      
            friend_request = FriendRequest.objects.get(id=friend_request_id, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'status': 'friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            friend_request.accepted = True
            friend_request.save()
            return Response({'status': 'friend request accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.rejected = True
            friend_request.save()
            return Response({'status': 'friend request rejected'}, status=status.HTTP_200_OK)

        return Response({'status': 'invalid action'}, status=status.HTTP_400_BAD_REQUEST)


class ListFriendsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(
            id__in=FriendRequest.objects.filter(from_user=self.request.user, accepted=True).values_list('to_user', flat=True)
        )

class ListPendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False, rejected=False)




class ThrottledFriendRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user_id  = request.data.get('friend_request_id')
        print(user_id,"is",CustomUser.objects.filter(id=user_id).exists())

        if  CustomUser.objects.filter(id=user_id).exists() == False:
            return Response({'status': 'friend id not found'}, status=status.HTTP_404_NOT_FOUND)

        key = f"friend_request_limit_{user_id}"
        last_request_time = cache.get(key, 0)
        current_time = time.time()

 
        if current_time - last_request_time < 60:  
            return Response({'status': 'too many requests'}, status=status.HTTP_429_TOO_MANY_REQUESTS)


        cache.set(key, current_time, timeout=60)

        return Response({'status': 'friend request sent successfully'}, status=status.HTTP_200_OK)


