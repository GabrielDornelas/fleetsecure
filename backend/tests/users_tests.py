from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from trucks.models import Truck
import json

class UserModelTests(TestCase):
    """Tests for the User model"""
    
    def test_create_user(self):
        """Test for user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.get_full_name(), 'Test User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_driver())
    
    def test_is_driver_method(self):
        """Test for the is_driver method"""
        user = User.objects.create_user(
            username='driveruser',
            email='driver@example.com',
            password='testpass123'
        )

        self.assertFalse(user.is_driver())

        user.license_number = 'XYZ12345'
        user.save()
        
        self.assertTrue(user.is_driver())
        
    def test_user_truck_relationship(self):
        """Test the relationship between users and trucks"""
        # Create a driver user
        driver = User.objects.create_user(
            username='driver1',
            email='driver1@example.com',
            password='driverpass',
            license_number='DRV12345'
        )
        
        # Create trucks for the driver
        truck1 = Truck.objects.create(
            user=driver,
            plate_number='ABC-1234',
            model='Volvo FH16',
            year=2022
        )
        
        truck2 = Truck.objects.create(
            user=driver,
            plate_number='DEF-5678',
            model='Scania R450',
            year=2023
        )
        
        # Check related trucks are accessible through the user
        user_trucks = driver.trucks.all()
        self.assertEqual(user_trucks.count(), 2)
        self.assertIn(truck1, user_trucks)
        self.assertIn(truck2, user_trucks)
        
        # Test cascade deletion - when user is deleted, trucks should be deleted too
        driver_id = driver.id
        truck1_id = truck1.id
        truck2_id = truck2.id
        
        driver.delete()
        
        # Verify user and associated trucks are deleted
        self.assertEqual(User.objects.filter(id=driver_id).count(), 0)
        self.assertEqual(Truck.objects.filter(id=truck1_id).count(), 0)
        self.assertEqual(Truck.objects.filter(id=truck2_id).count(), 0)


class UserAPITests(APITestCase):
    """Tests for the User API"""
    
    def setUp(self):
        """Initial setup for tests"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )
        
        # Create normal user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a driver with trucks
        self.driver = User.objects.create_user(
            username='driver',
            email='driver@example.com',
            password='driverpass',
            license_number='DRV12345'
        )
        
        # Create trucks for the driver
        self.truck1 = Truck.objects.create(
            user=self.driver,
            plate_number='ABC-1234',
            model='Volvo FH16',
            year=2022
        )
        
        self.truck2 = Truck.objects.create(
            user=self.driver,
            plate_number='DEF-5678',
            model='Scania R450',
            year=2023
        )
        
        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.users_list_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', kwargs={'pk': self.user.id})
        self.driver_detail_url = reverse('user-detail', kwargs={'pk': self.driver.id})
        self.user_me_url = reverse('user-me')
        
    def get_tokens_for_user(self, user):
        """Get JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_login(self):
        """Test for login endpoint (token obtaining)"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_list_admin_access(self):
        """Test for listing users (admin access)"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 3)  # Should have at least the three created users
    
    def test_user_list_normal_user_denied(self):
        """Test for listing users (access denied for normal user)"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_detail_self_access(self):
        """Test for retrieving details of own user"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_detail_admin_access(self):
        """Test for retrieving details of another user as admin"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_me_endpoint(self):
        """Test for the /me endpoint"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_create_user(self):
        """Test for creating a new user"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.users_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
    
    def test_update_user_self(self):
        """Test for updating own user"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that changes were applied
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_update_user_admin(self):
        """Test for updating another user as admin"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'first_name': 'Admin',
            'last_name': 'Updated'
        }
        response = self.client.patch(self.user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that changes were applied
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Admin')
        self.assertEqual(self.user.last_name, 'Updated')
    
    def test_change_password(self):
        """Test for changing password"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('user-change-password', kwargs={'pk': self.user.id})
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that the password was changed by trying to login
        self.client.credentials()  # Clear credentials
        login_data = {
            'username': 'testuser',
            'password': 'newpass456'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_activate_deactivate_user(self):
        """Test for activating and deactivating a user (admin)"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Deactivate user
        url = reverse('user-deactivate', kwargs={'pk': self.user.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the user was deactivated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Activate user
        url = reverse('user-activate', kwargs={'pk': self.user.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the user was activated
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
    def test_delete_user_with_trucks(self):
        """Test deleting a user with associated trucks via API"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Store truck IDs to verify deletion
        truck_ids = [self.truck1.id, self.truck2.id]
        
        # Delete the driver
        response = self.client.delete(self.driver_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify driver was deleted
        self.assertEqual(User.objects.filter(username='driver').count(), 0)
        
        # Verify associated trucks were deleted (cascade)
        for truck_id in truck_ids:
            self.assertEqual(Truck.objects.filter(id=truck_id).count(), 0)
            
    def test_driver_with_trucks_representation(self):
        """Test that driver details are properly shown when requesting a truck"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Get truck details through the trucks API
        trucks_url = reverse('truck-detail', kwargs={'pk': self.truck1.id})
        response = self.client.get(trucks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user details are included
        self.assertIn('user_details', response.data)
        self.assertEqual(response.data['user_details']['username'], 'driver')
        self.assertEqual(response.data['user_details']['license_number'], 'DRV12345')
