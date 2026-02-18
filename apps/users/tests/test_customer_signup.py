from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Customer


class CustomerSignupViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users:customer-signup')
        self.valid_payload = {
            'full_name': 'João Silva',
            'email': 'joao@example.com',
            'phone': '(11) 99999-9999',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }

    def test_signup_creates_user_and_customer(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='joao@example.com').exists())
        user = User.objects.get(email='joao@example.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_signup_returns_user_data(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['email'], 'joao@example.com')
        self.assertEqual(data['full_name'], 'João Silva')
        self.assertEqual(data['user_type'], 'customer')
        self.assertNotIn('password', data)

    def test_signup_rejects_duplicate_email(self):
        self.client.post(self.url, self.valid_payload, format='json')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_signup_rejects_password_mismatch(self):
        payload = {**self.valid_payload, 'confirm_password': 'WrongPass123!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.json())

    def test_signup_rejects_missing_required_fields(self):
        for field in ['full_name', 'email', 'phone', 'password', 'confirm_password']:
            payload = {k: v for k, v in self.valid_payload.items() if k != field}
            response = self.client.post(self.url, payload, format='json')
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                msg=f'Expected 400 when {field!r} is missing',
            )
            self.assertIn(field, response.json())

    def test_signup_rejects_invalid_email(self):
        payload = {**self.valid_payload, 'email': 'not-an-email'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_signup_normalises_email_to_lowercase(self):
        payload = {**self.valid_payload, 'email': 'Joao@EXAMPLE.COM'}
        self.client.post(self.url, payload, format='json')
        self.assertTrue(User.objects.filter(email='joao@example.com').exists())

    def test_signup_rejects_weak_password(self):
        payload = {**self.valid_payload, 'password': '123', 'confirm_password': '123'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.json())


class CustomerSignupSerializerTests(TestCase):
    def _make_serializer(self, data):
        from users.serializers import CustomerSignupSerializer
        return CustomerSignupSerializer(data=data)

    def test_valid_data_is_accepted(self):
        s = self._make_serializer({
            'full_name': 'Maria Souza',
            'email': 'maria@example.com',
            'phone': '(21) 88888-8888',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_passwords_must_match(self):
        s = self._make_serializer({
            'full_name': 'Maria Souza',
            'email': 'maria@example.com',
            'phone': '(21) 88888-8888',
            'password': 'StrongPass123!',
            'confirm_password': 'DifferentPass123!',
        })
        self.assertFalse(s.is_valid())
        self.assertIn('confirm_password', s.errors)

    def test_create_returns_customer_instance(self):
        s = self._make_serializer({
            'full_name': 'Pedro Lima',
            'email': 'pedro@example.com',
            'phone': '(31) 77777-7777',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        })
        self.assertTrue(s.is_valid(), s.errors)
        customer = s.save()
        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.user.email, 'pedro@example.com')
