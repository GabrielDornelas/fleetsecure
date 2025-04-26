from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Driver
from users.models import User
import json

class DriverModelTests(TestCase):
    """Testes para o modelo Driver"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testdriver',
            email='driver@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Driver'
        )
    
    def test_create_driver(self):
        """Teste para criação de driver"""
        driver = Driver.objects.create(
            user=self.user,
            license_number='XYZ12345',
            is_active=True
        )
        self.assertEqual(driver.user, self.user)
        self.assertEqual(driver.license_number, 'XYZ12345')
        self.assertTrue(driver.is_active)
        
        # Verificar se o método is_driver do usuário retorna True
        self.assertTrue(self.user.is_driver())
    
    def test_driver_string_representation(self):
        """Teste para a representação string do driver"""
        driver = Driver.objects.create(
            user=self.user,
            license_number='XYZ12345'
        )
        self.assertEqual(str(driver), 'Test Driver')


class DriverAPITests(APITestCase):
    """Testes para a API de drivers"""
    
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
        
        # Criar usuário driver
        self.driver_user = User.objects.create_user(
            username='driveruser',
            email='driver@example.com',
            password='driverpass',
            first_name='Driver',
            last_name='User'
        )
        
        # Criar driver
        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number='ABC12345',
            is_active=True
        )
        
        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.drivers_list_url = reverse('driver-list')
        self.driver_detail_url = reverse('driver-detail', kwargs={'pk': self.driver.id})
        self.driver_me_url = reverse('driver-me')
        
    def get_tokens_for_user(self, user):
        """Obter tokens JWT para um usuário"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_list_drivers(self):
        """Teste para listar drivers"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.drivers_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)  # Deve ter pelo menos um driver
    
    def test_retrieve_driver(self):
        """Teste para obter detalhes de um driver"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.driver_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], 'ABC12345')
        self.assertEqual(response.data['user']['username'], 'driveruser')
    
    def test_driver_me_endpoint(self):
        """Teste para o endpoint /me quando o usuário é driver"""
        # Autenticar como usuário driver
        tokens = self.get_tokens_for_user(self.driver_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.driver_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], 'ABC12345')
    
    def test_driver_me_endpoint_not_driver(self):
        """Teste para o endpoint /me quando o usuário não é driver"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.driver_me_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_driver(self):
        """Teste para criar um novo driver"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'username': 'newdriver',
            'first_name': 'New',
            'last_name': 'Driver',
            'email': 'newdriver@example.com',
            'password': 'driverpass123',
            'license_number': 'DRV98765'
        }
        response = self.client.post(self.drivers_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se o driver foi criado
        self.assertTrue(Driver.objects.filter(license_number='DRV98765').exists())
        
        # Verificar se o usuário foi criado
        user = User.objects.get(username='newdriver')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Driver')
        self.assertTrue(user.is_driver())
    
    def test_update_driver(self):
        """Teste para atualizar um driver"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'license_number': 'UPDATED123'
        }
        response = self.client.patch(self.driver_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se as alterações foram aplicadas
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.license_number, 'UPDATED123')
    
    def test_activate_deactivate_driver(self):
        """Teste para ativar e desativar driver"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Desativar driver
        url = reverse('driver-deactivate', kwargs={'pk': self.driver.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se o driver foi desativado
        self.driver.refresh_from_db()
        self.assertFalse(self.driver.is_active)
        
        # Ativar driver
        url = reverse('driver-activate', kwargs={'pk': self.driver.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se o driver foi ativado
        self.driver.refresh_from_db()
        self.assertTrue(self.driver.is_active)
