from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from startups.models import (
    Application,
    Bookmark,
    Category,
    Startup,
    StartupMember,
    Vacancy,
    FOUNDER,
    DEVELOPER,
)


def make_user(username, email, **extra):
    return CustomUser.objects.create_user(
        username=username,
        email=email,
        password="StrongPass123!",
        **extra,
    )


class StartupApiTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin", "admin@example.com", is_staff=True)
        self.owner = make_user("owner", "owner@example.com")
        self.other = make_user("other", "other@example.com")
        self.user = make_user("user", "user@example.com")
        self.category = Category.objects.create(name="AI", slug="ai")
        self.startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
            is_public=True,
        )
        StartupMember.objects.create(startup=self.startup, user=self.owner, role=FOUNDER)

    def test_category_create_exists_for_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/startups/categories/",
            {"name": "Fintech", "slug": "fintech"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="fintech").exists())

    def test_startup_detail_uses_uuid_pk_and_non_owner_cannot_patch(self):
        detail_url = f"/startups/{self.startup.id}/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.other)
        response = self.client.patch(detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.title, "Alpha")

    def test_private_startup_is_hidden_from_other_users(self):
        self.startup.is_public = False
        self.startup.save(update_fields=["is_public"])

        self.client.force_authenticate(self.user)
        response = self.client.get(f"/startups/{self.startup.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_any_authenticated_user_can_create_startup_and_becomes_founder(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/startups/",
            {
                "title": "NewOne",
                "slug": "newone",
                "short_description": "Short",
                "description": "Long",
                "category": str(self.category.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Startup.objects.filter(slug="newone").exists())
        self.assertTrue(
            StartupMember.objects.filter(
                user=self.user, role=FOUNDER, startup__slug="newone"
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_startup(self):
        response = self.client.post(
            "/startups/",
            {
                "title": "Anon",
                "slug": "anon",
                "short_description": "Short",
                "description": "Long",
                "category": str(self.category.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Startup.objects.filter(slug="anon").exists())


class BookmarkApiTests(APITestCase):
    def setUp(self):
        self.user = make_user("user", "user@example.com")
        self.owner = make_user("owner", "owner@example.com")
        self.category = Category.objects.create(name="AI", slug="ai")
        self.startup = Startup.objects.create(
            owner=self.owner,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
        )

    def test_bookmark_create_list_and_delete(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/startups/bookmarks/",
            {"startup_id": str(self.startup.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Bookmark.objects.filter(user=self.user, startup=self.startup).exists()
        )

        response = self.client.get("/startups/bookmarks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f"/startups/bookmarks/{self.startup.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Bookmark.objects.filter(user=self.user, startup=self.startup).exists()
        )

    def test_duplicate_bookmark_is_idempotent(self):
        self.client.force_authenticate(self.user)
        for _ in range(2):
            response = self.client.post(
                "/startups/bookmarks/",
                {"startup_id": str(self.startup.id)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)


class VacancyApplyFlowTests(APITestCase):
    def setUp(self):
        self.founder = make_user("founder", "founder@example.com")
        self.outsider = make_user("outsider", "outsider@example.com")
        self.applicant = make_user("applicant", "applicant@example.com")
        self.category = Category.objects.create(name="AI", slug="ai")
        self.startup = Startup.objects.create(
            owner=self.founder,
            category=self.category,
            title="Alpha",
            slug="alpha",
            short_description="Short",
            description="Long",
        )
        StartupMember.objects.create(
            startup=self.startup, user=self.founder, role=FOUNDER
        )

    def test_non_founder_cannot_open_vacancy(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            f"/startups/{self.startup.id}/vacancies/",
            {
                "title": "Backend dev",
                "role": DEVELOPER,
                "description": "Django experience",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vacancy.objects.count(), 0)

    def test_founder_opens_vacancy_and_applicant_applies(self):
        self.client.force_authenticate(self.founder)
        response = self.client.post(
            f"/startups/{self.startup.id}/vacancies/",
            {
                "title": "Backend dev",
                "role": DEVELOPER,
                "description": "Django experience",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        vacancy_id = response.data["id"]

        self.client.force_authenticate(self.applicant)
        response = self.client.post(
            f"/startups/vacancies/{vacancy_id}/applications/",
            {"message": "I am interested"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application = Application.objects.get()
        self.assertEqual(application.applicant, self.applicant)
        self.assertEqual(application.status, Application.PENDING)

    def test_founder_can_accept_application_and_it_becomes_member(self):
        vacancy = Vacancy.objects.create(
            startup=self.startup,
            title="Backend",
            role=DEVELOPER,
            description="Work",
        )
        application = Application.objects.create(
            vacancy=vacancy, applicant=self.applicant, message="hi"
        )

        self.client.force_authenticate(self.founder)
        response = self.client.patch(
            f"/startups/applications/{application.id}/",
            {"status": Application.ACCEPTED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.ACCEPTED)
        self.assertTrue(
            StartupMember.objects.filter(
                startup=self.startup, user=self.applicant, role=DEVELOPER
            ).exists()
        )

    def test_duplicate_application_is_blocked(self):
        vacancy = Vacancy.objects.create(
            startup=self.startup,
            title="Backend",
            role=DEVELOPER,
            description="Work",
        )
        self.client.force_authenticate(self.applicant)
        first = self.client.post(
            f"/startups/vacancies/{vacancy.id}/applications/",
            {"message": "first"},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(
            f"/startups/vacancies/{vacancy.id}/applications/",
            {"message": "second"},
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(Application.objects.count(), 1)
