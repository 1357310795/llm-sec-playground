import uuid

from django.db import models


class Scenario(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    id = models.SlugField(primary_key=True, max_length=80)
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    difficulty = models.CharField(max_length=16, choices=Difficulty.choices, default=Difficulty.EASY)
    summary = models.TextField()
    chapter_refs = models.JSONField(default=list)
    learning_goals = models.JSONField(default=list)
    allowed_inputs = models.JSONField(default=list)
    system_prompt = models.TextField(blank=True)
    training_targets = models.JSONField(default=list)
    success_conditions = models.JSONField(default=list)
    hints = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class DefenseProfile(models.Model):
    scenario = models.OneToOneField(Scenario, on_delete=models.CASCADE, related_name="default_defenses")
    input_moderation = models.BooleanField(default=True)
    prompt_injection_detection = models.BooleanField(default=True)
    encoding_normalization = models.BooleanField(default=True)
    instruction_data_separation = models.BooleanField(default=True)
    output_moderation = models.BooleanField(default=True)
    tool_policy_enforcement = models.BooleanField(default=True)
    human_confirmation_required = models.BooleanField(default=True)
    rate_limit = models.BooleanField(default=False)

    def as_camel_dict(self):
        return {
            "inputModeration": self.input_moderation,
            "promptInjectionDetection": self.prompt_injection_detection,
            "encodingNormalization": self.encoding_normalization,
            "instructionDataSeparation": self.instruction_data_separation,
            "outputModeration": self.output_moderation,
            "toolPolicyEnforcement": self.tool_policy_enforcement,
            "humanConfirmationRequired": self.human_confirmation_required,
            "rateLimit": self.rate_limit,
        }


class ScenarioDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=160)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    is_poisoned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Attempt(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"
        PENDING_CONFIRMATION = "pending_confirmation", "Pending confirmation"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="attempts")
    session_id = models.CharField(max_length=120, default="demo-session")
    messages = models.JSONField(default=list)
    submitted_text = models.TextField(blank=True)
    submitted_schema = models.JSONField(null=True, blank=True)
    submitted_documents = models.JSONField(default=list)
    defense_overrides = models.JSONField(default=dict)
    retrieved_docs = models.JSONField(default=list)
    tool_calls = models.JSONField(default=list)
    model_output = models.TextField(blank=True)
    safe_output = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.COMPLETED)
    timeline = models.JSONField(default=list)
    repair_advice = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class RiskEvent(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Action(models.TextChoices):
        ALLOWED = "allowed", "Allowed"
        FLAGGED = "flagged", "Flagged"
        NORMALIZED = "normalized", "Normalized"
        SANITIZED = "sanitized", "Sanitized"
        BLOCKED = "blocked", "Blocked"
        CONFIRMATION_REQUIRED = "confirmation_required", "Confirmation required"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="risk_events")
    type = models.CharField(max_length=80)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    source = models.CharField(max_length=80)
    message = models.CharField(max_length=240)
    span = models.CharField(max_length=180, blank=True)
    action = models.CharField(max_length=32, choices=Action.choices)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
