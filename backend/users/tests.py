from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import json

class UserModelTests(TestCase):
    """Testes para o modelo User"""
    
    def test_create_user(self):
        """Teste para criação de usuário"""
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
        """Teste para o método is_driver"""
        user = User.objects.create_user(
            username='driveruser',
            email='driver@example.com',
            password='testpass123'
        )
        # Inicialmente não é um driver
        self.assertFalse(user.is_driver())
        
        # Deve retornar True quando o usuário tiver um driver associado
        # Note: precisaremos do modelo Driver, mas isso será testado no app drivers


class UserAPITests(APITestCase):
    """Testes para a API de usuários"""
    
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
        
        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.users_list_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', kwargs={'pk': self.user.id})
        self.user_me_url = reverse('user-me')
        
    def get_tokens_for_user(self, user):
        """Obter tokens JWT para um usuário"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_login(self):
        """Teste para o endpoint de login (obtenção de token)"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_list_admin_access(self):
        """Teste para listar usuários (acesso de admin)"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)  # Deve ter pelo menos os dois usuários criados
    
    def test_user_list_normal_user_denied(self):
        """Teste para listar usuários (acesso negado para usuário normal)"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_detail_self_access(self):
        """Teste para obter detalhes do próprio usuário"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_detail_admin_access(self):
        """Teste para obter detalhes de outro usuário como admin"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_me_endpoint(self):
        """Teste para o endpoint /me"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_create_user(self):
        """Teste para criar um novo usuário"""
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
        """Teste para atualizar o próprio usuário"""
        # Autenticar como usuário normal
        tokens = self.get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se as alterações foram aplicadas
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_update_user_admin(self):
        """Teste para atualizar outro usuário como admin"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        data = {
            'first_name': 'Admin',
            'last_name': 'Updated'
        }
        response = self.client.patch(self.user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se as alterações foram aplicadas
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Admin')
        self.assertEqual(self.user.last_name, 'Updated')
    
    def test_change_password(self):
        """Teste para alterar senha"""
        # Autenticar como usuário normal
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
        
        # Verificar se a senha foi alterada tentando fazer login
        self.client.credentials()  # Limpar credenciais
        login_data = {
            'username': 'testuser',
            'password': 'newpass456'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_activate_deactivate_user(self):
        """Teste para ativar e desativar usuário (admin)"""
        # Autenticar como admin
        tokens = self.get_tokens_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Desativar usuário
        url = reverse('user-deactivate', kwargs={'pk': self.user.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se o usuário foi desativado
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Ativar usuário
        url = reverse('user-activate', kwargs={'pk': self.user.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se o usuário foi ativado
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
