from django.db import models
from accounts.models import CustomUser
from shared.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


IDEA = "idea"
MVP = "mvp"
BETA = "beta"
LAUNCHED = "launched"
CLOSED = "closed"


class Startup(BaseModel):
    STAGE_CHOICES = (
        (IDEA, "Idea"),
        (MVP, "MVP"),
        (BETA, "Beta"),
        (LAUNCHED, "Launched"),
        (CLOSED, "Closed"),
    )

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="startups")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="startups")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    logo = models.ImageField(upload_to="startup/logo/", blank=True, null=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    demo = models.URLField(blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=IDEA)
    tags = models.ManyToManyField(Tag, blank=True, related_name="startups")
    views = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    is_open_source = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class StartupImage(BaseModel):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="startup/images/")


class Bookmark(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookmarks")
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="bookmarks")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "startup"],
                name="unique_bookmark"
            )
        ]


FOUNDER = "founder"
COFOUNDER = "cofounder"
DEVELOPER = "developer"
DESIGNER = "designer"
PRODUCT_MANAGER = "product_manager"
MARKETER = "marketer"
SALES = "sales"
DEVOPS = "devops"
QA = "qa"
ADVISOR = "advisor"
MENTOR = "mentor"

ROLE_CHOICES = (

    (FOUNDER, "Founder"),
    (COFOUNDER, "Co-Founder"),
    (DEVELOPER, "Developer"),
    (DESIGNER, "Designer"),
    (PRODUCT_MANAGER, "Product Manager"),
    (MARKETER, "Marketing Specialist"),
    (SALES, "Sales"),
    (DEVOPS, "DevOps"),
    (QA, "QA Engineer"),
    (ADVISOR, "Advisor"),
    (MENTOR, "Mentor"),

)

class StartupMember(BaseModel):
    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name="members"
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=30,choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["startup", "user"],
                name="unique_member"
            )
        ]


class Vacancy(BaseModel):
    OPEN = "open"
    CLOSED = "closed"

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (CLOSED, "Closed"),
    )

    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="vacancies")
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.startup.title}"


class Application(BaseModel):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vacancy", "applicant"],
                name="unique_application_per_vacancy",
            )
        ]

    def __str__(self):
        return f"{self.applicant} -> {self.vacancy.title}"
