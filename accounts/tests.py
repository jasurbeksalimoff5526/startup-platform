from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from accounts.profiles import InvestorProfile, MentorProfile


class ProfileApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123!",
        )

    def test_mentor_profile_is_auto_created_on_first_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/auth/mentor-profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(MentorProfile.objects.filter(user=self.user).exists())

    def test_mentor_profile_can_be_updated(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            "/auth/mentor-profile/",
            {
                "expertise": "Backend engineering",
                "years_of_experience": 7,
                "available": True,
                "hourly_rate": "50.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = MentorProfile.objects.get(user=self.user)
        self.assertEqual(profile.expertise, "Backend engineering")
        self.assertEqual(profile.years_of_experience, 7)

    def test_investor_profile_is_auto_created_on_first_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/auth/investor-profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(InvestorProfile.objects.filter(user=self.user).exists())

    def test_investor_profile_validates_ticket_range(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            "/auth/investor-profile/",
            {
                "company": "Acme",
                "bio": "Series A",
                "min_ticket": "50000",
                "max_ticket": "10000",
                "industries": ["SaaS"],
                "countries": ["UZ"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_investor_profile_can_be_updated(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            "/auth/investor-profile/",
            {
                "company": "Acme",
                "bio": "Series A",
                "min_ticket": "10000",
                "max_ticket": "50000",
                "industries": ["SaaS"],
                "countries": ["UZ"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = InvestorProfile.objects.get(user=self.user)
        self.assertEqual(profile.company, "Acme")
        self.assertEqual(profile.industries, ["SaaS"])

    def test_unauthenticated_cannot_access_profiles(self):
        response = self.client.get("/auth/mentor-profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get("/auth/investor-profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
