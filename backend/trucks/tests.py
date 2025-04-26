from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Truck
from drivers.models import Driver
from users.models import User
import json

class TruckModelTests(TestCase):
    """Testes para o modelo Truck"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para driver
        self.user = User.objects.create_user(
            username='driveruser',
            email='driver@example.com',
            password='driverpass',
            first_name='Driver',
            last_name='User'
        )
        
        # Criar driver
        self.driver = Driver.objects.create(
            user=self.user,
            license_number='ABC12345',
            is_active=True
        )
    
    def test_create_truck(self):
        """Teste para criação de caminhão"""
        truck = Truck.objects.create(
            driver=self.driver,
            plate_number='XYZ-1234',
            model='Scania R450',
            year=2023
        )
        self.assertEqual(truck.driver, self.driver)
        self.assertEqual(truck.plate_number, 'XYZ-1234')
        self.assertEqual(truck.model, 'Scania R450')
        self.assertEqual(truck.year, 2023)
    
    def test_truck_string_representation(self):
        """Teste para a representação string do caminhão"""
        truck = Truck.objects.create(
            driver=self.driver,
            plate_number='XYZ-1234',
            model='Scania R450',
            year=2023
        )
        self.assertEqual(str(truck), 'Scania R450 - XYZ-1234')


class TruckAPITests(APITestCase):
    """Testes para a API de caminhões"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = APIClient()
        
        # Criar usuário admin
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )
        
        # Criar usuário normal
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Criar usuário driver 1
        self.driver_user1 = User.objects.create_user(
            username='driver1',
            email='driver1@example.com',
            password='driver1pass',
            first_name='Driver',
            last_name='One'
        )
        
        # Criar driver 1
        self.driver1 = Driver.objects.create(
            user=self.driver_user1,
            license_number='DRV-001',
            is_active=True
        )
        
        # Criar usuário driver 2
        self.driver_user2 = User.objects.create_user(
            username='driver2',
            email='driver2@example.com',
            password='driver2pass',
            first_name='Driver',
            last_name='Two'
        )
        
        # Criar driver 2
        self.driver2 = Driver.objects.create(
            user=self.driver_user2,
            license_number='DRV-002',
            is_active=True
        )
        
        # Criar caminhões
        self.truck1 = Truck.objects.create(
            driver=self.driver1,
            plate_number='ABC-1234',
            model='Volvo FH16',
            year=2022
        )
        
        self.truck2 = Truck.objects.create(
            driver=self.driver2,
            plate_number='DEF-5678',
            model='Mercedes Actros',
            year=2023
        )
        
        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.trucks_list_url = reverse('truck-list')
        self.truck_detail_url = reverse('truck-detail', kwargs={'pk': self.truck1.id})
        self.by_driver_url = reverse('truck-by-driver')
        self.by_year_url = reverse('truck-by-year')
        
    def get_tokens_for_user(self, user):
        """Obter tokens JWT para um usuário"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_list_trucks(self):
        """Teste para listar caminhões"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.trucks_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Deve ter 2 caminhões
    
    def test_retrieve_truck(self):
        """Teste para obter detalhes de um caminhão"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.truck_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plate_number'], 'ABC-1234')
        self.assertEqual(response.data['model'], 'Volvo FH16')
        self.assertEqual(response.data['year'], 2022)
        self.assertEqual(response.data['driver_details']['license_number'], 'DRV-001')
    
    def test_create_truck(self):
        """Teste para criar um novo caminhão"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'driver': self.driver1.id,
            'plate_number': 'GHI-9012',
            'model': 'Scania S730',
            'year': 2024
        }
        response = self.client.post(self.trucks_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se o caminhão foi criado
        self.assertTrue(Truck.objects.filter(plate_number='GHI-9012').exists())
        truck = Truck.objects.get(plate_number='GHI-9012')
        self.assertEqual(truck.driver, self.driver1)
        self.assertEqual(truck.model, 'Scania S730')
        self.assertEqual(truck.year, 2024)
    
    def test_update_truck(self):
        """Teste para atualizar um caminhão"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'plate_number': 'UPDATED',
            'year': 2025
        }
        response = self.client.patch(self.truck_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se as alterações foram aplicadas
        self.truck1.refresh_from_db()
        self.assertEqual(self.truck1.plate_number, 'UPDATED')
        self.assertEqual(self.truck1.year, 2025)
    
    def test_delete_truck(self):
        """Teste para excluir um caminhão"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.delete(self.truck_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar se o caminhão foi excluído
        self.assertFalse(Truck.objects.filter(id=self.truck1.id).exists())
    
    def test_filter_trucks_by_driver(self):
        """Teste para filtrar caminhões por motorista"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Filtrar caminhões pelo driver1
        response = self.client.get(f'{self.by_driver_url}?driver_id={self.driver1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'ABC-1234')
        
        # Filtrar caminhões pelo driver2
        response = self.client.get(f'{self.by_driver_url}?driver_id={self.driver2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'DEF-5678')
    
    def test_filter_trucks_by_year(self):
        """Teste para filtrar caminhões por ano"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Filtrar caminhões do ano 2022
        response = self.client.get(f'{self.by_year_url}?year=2022')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'ABC-1234')
        
        # Filtrar caminhões do ano 2023
        response = self.client.get(f'{self.by_year_url}?year=2023')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate_number'], 'DEF-5678')
    
    def test_fail_filters_without_parameters(self):
        """Teste para garantir que os filtros falhem quando parâmetros obrigatórios não são fornecidos"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Tentar filtrar por driver sem fornecer driver_id
        response = self.client.get(self.by_driver_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Tentar filtrar por ano sem fornecer year
        response = self.client.get(self.by_year_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
