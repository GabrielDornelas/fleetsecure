from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from trucks.models import Truck
from users.models import User
import json

class TruckModelTests(TestCase):
    """Tests for the Truck model"""
    
    def setUp(self):
        """Initial setup for tests"""
        # Create user with driver license
        self.user = User.objects.create_user(
            username='useruser',
            email='user@example.com',
            password='userpass',
            first_name='Driver',
            last_name='User',
            license_number='ABC12345',
            is_active=True
        )

        # Create user without license
        self.non_driver_user = User.objects.create_user(
            username='nondriver',
            email='nondriver@example.com',
            password='userpass',
            first_name='Non',
            last_name='Driver',
            is_active=True
        )

    
    def test_create_truck(self):
        """Test for truck creation"""
        truck = Truck.objects.create(
            user=self.user,
            plate_number='XYZ-1234',
            model='Scania R450',
            year=2023
        )
        self.assertEqual(truck.user, self.user)
        self.assertEqual(truck.plate_number, 'XYZ-1234')
        self.assertEqual(truck.model, 'Scania R450')
        self.assertEqual(truck.year, 2023)
    
    def test_truck_string_representation(self):
        """Test for the truck string representation"""
        truck = Truck.objects.create(
            user=self.user,
            plate_number='XYZ-1234',
            model='Scania R450',
            year=2023
        )
        self.assertEqual(str(truck), 'Scania R450 - XYZ-1234')
        
    def test_create_truck_with_non_driver_user(self):
        """Test for creating a truck with a user that doesn't have a license"""
        # System should allow this, as business rules might be enforced at a higher level
        truck = Truck.objects.create(
            user=self.non_driver_user,
            plate_number='ABC-9876',
            model='Volvo FH',
            year=2022
        )
        self.assertEqual(truck.user, self.non_driver_user)
        self.assertEqual(truck.plate_number, 'ABC-9876')
        # Verify the user doesn't have a license
        self.assertFalse(self.non_driver_user.is_driver())


class TruckAPITests(APITestCase):
    """Tests for the Truck API"""
    
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
            last_name='User',
            license_number='DRV-001',
            is_active=True
        )
        
        # Create user driver 1
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass',
            first_name='Driver',
            last_name='One',
            license_number='DRV-003',
            is_active=True
        )

        # Create user driver 2
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass',
            first_name='Driver',
            last_name='Two',
            license_number='DRV-002',
            is_active=True
        )
        
        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='inactive123',
            first_name='Inactive',
            last_name='User',
            license_number='DRV-004',
            is_active=False
        )

        # Create trucks
        self.truck1 = Truck.objects.create(
            user=self.user1,
            plate_number='ABC-1234',
            model='Volvo FH16',
            year=2022
        )
        
        self.truck2 = Truck.objects.create(
            user=self.user2,
            plate_number='DEF-5678',
            model='Mercedes Actros',
            year=2023
        )
        
        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.trucks_list_url = reverse('truck-list')
        self.truck_detail_url = reverse('truck-detail', kwargs={'pk': self.truck1.id})
        self.by_user_url = reverse('truck-by-user')
        self.by_year_url = reverse('truck-by-year')
        
    def get_tokens_for_user(self, user):
        """Get JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_list_trucks(self):
        """Test for listing trucks"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.trucks_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have 2 trucks
    
    def test_retrieve_truck(self):
        """Test for retrieving truck details"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.truck_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plate_number'], 'ABC-1234')
        self.assertEqual(response.data['model'], 'Volvo FH16')
        self.assertEqual(response.data['year'], 2022)
        self.assertEqual(response.data['user_details']['license_number'], 'DRV-003')
    
    def test_create_truck(self):
        """Test for creating a new truck"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'user': self.user1.id,
            'plate_number': 'GHI-9012',
            'model': 'Scania S730',
            'year': 2024
        }
        response = self.client.post(self.trucks_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the truck was created
        self.assertTrue(Truck.objects.filter(plate_number='GHI-9012').exists())
        truck = Truck.objects.get(plate_number='GHI-9012')
        self.assertEqual(truck.user, self.user1)
        self.assertEqual(truck.model, 'Scania S730')
        self.assertEqual(truck.year, 2024)
    
    def test_update_truck(self):
        """Test for updating a truck"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'plate_number': 'UPDATED',
            'year': 2025
        }
        response = self.client.patch(self.truck_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify changes were applied
        self.truck1.refresh_from_db()
        self.assertEqual(self.truck1.plate_number, 'UPDATED')
        self.assertEqual(self.truck1.year, 2025)
    
    def test_delete_truck(self):
        """Test for deleting a truck"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.delete(self.truck_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the truck was deleted
        self.assertFalse(Truck.objects.filter(id=self.truck1.id).exists())
    
    def test_filter_trucks_by_user(self):
        """Test for filtering trucks by user"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Filter trucks by user1
        response = self.client.get(f'{self.by_user_url}?user_id={self.user1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'ABC-1234')
        
        # Filter trucks by user2
        response = self.client.get(f'{self.by_user_url}?user_id={self.user2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'DEF-5678')
    
    def test_filter_trucks_by_year(self):
        """Test for filtering trucks by year"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Filter trucks from year 2022
        response = self.client.get(f'{self.by_year_url}?year=2022')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'ABC-1234')
        
        # Filter trucks from year 2023
        response = self.client.get(f'{self.by_year_url}?year=2023')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'DEF-5678')
    
    def test_fail_filters_without_parameters(self):
        """Test to ensure filters fail when required parameters are not provided"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Try to filter by user without providing user_id
        response = self.client.get(self.by_user_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Try to filter by year without providing year
        response = self.client.get(self.by_year_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_truck_for_inactive_user(self):
        """Test creating a truck for an inactive user"""
        # Authenticate as admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'user': self.inactive_user.id,
            'plate_number': 'ABC-123',
            'model': 'Iveco Daily',
            'year': 2021
        }
        response = self.client.post(self.trucks_list_url, data, format='json')
        
        # The API should now reject creating a truck for an inactive user
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)  # Error message should mention the user field
        
    def test_filter_truck_with_nonexistent_user(self):
        """Test filtering trucks with a non-existent user ID"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Use an ID that doesn't exist
        non_existent_id = 99999
        response = self.client.get(f'{self.by_user_url}?user_id={non_existent_id}')
        
        # It should return an empty list, not an error
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_filter_truck_with_year_no_results(self):
        """Test filtering trucks with a year that has no trucks"""
        # Authenticate as normal user
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Use a year with no trucks
        future_year = 2050
        response = self.client.get(f'{self.by_year_url}?year={future_year}')
        
        # It should return an empty list, not an error
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
