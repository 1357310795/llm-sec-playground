from rest_framework import serializers

from .models import Attempt, DefenseProfile, RiskEvent, Scenario, ScenarioDocument


class DefenseProfileSerializer(serializers.ModelSerializer):
    inputModeration = serializers.BooleanField(source="input_moderation")
    promptInjectionDetection = serializers.BooleanField(source="prompt_injection_detection")
    encodingNormalization = serializers.BooleanField(source="encoding_normalization")
    instructionDataSeparation = serializers.BooleanField(source="instruction_data_separation")
    outputModeration = serializers.BooleanField(source="output_moderation")
    toolPolicyEnforcement = serializers.BooleanField(source="tool_policy_enforcement")
    humanConfirmationRequired = serializers.BooleanField(source="human_confirmation_required")
    rateLimit = serializers.BooleanField(source="rate_limit")

    class Meta:
        model = DefenseProfile
        fields = [
            "inputModeration",
            "promptInjectionDetection",
            "encodingNormalization",
            "instructionDataSeparation",
            "outputModeration",
            "toolPolicyEnforcement",
            "humanConfirmationRequired",
            "rateLimit",
        ]


class ScenarioListSerializer(serializers.ModelSerializer):
    chapterRefs = serializers.JSONField(source="chapter_refs")
    learningGoals = serializers.JSONField(source="learning_goals")
    allowedInputs = serializers.JSONField(source="allowed_inputs")
    trainingTargets = serializers.JSONField(source="training_targets")
    defaultDefenses = DefenseProfileSerializer(source="default_defenses")

    class Meta:
        model = Scenario
        fields = [
            "id",
            "title",
            "category",
            "difficulty",
            "summary",
            "chapterRefs",
            "learningGoals",
            "allowedInputs",
            "trainingTargets",
            "defaultDefenses",
        ]


class ScenarioDetailSerializer(ScenarioListSerializer):
    successConditions = serializers.JSONField(source="success_conditions")
    hints = serializers.JSONField()

    class Meta(ScenarioListSerializer.Meta):
        fields = ScenarioListSerializer.Meta.fields + ["successConditions", "hints"]


class RiskEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskEvent
        fields = ["type", "severity", "source", "message", "span", "action", "metadata"]


class ScenarioDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioDocument
        fields = ["id", "title", "content", "metadata", "is_poisoned", "created_at"]
        read_only_fields = ["id", "is_poisoned", "created_at"]


class AttemptSerializer(serializers.ModelSerializer):
    attemptId = serializers.UUIDField(source="id")
    scenarioId = serializers.CharField(source="scenario_id")
    modelOutput = serializers.CharField(source="model_output")
    safeOutput = serializers.CharField(source="safe_output")
    riskEvents = RiskEventSerializer(source="risk_events", many=True)
    retrievedDocs = serializers.JSONField(source="retrieved_docs")
    toolCalls = serializers.JSONField(source="tool_calls")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Attempt
        fields = [
            "attemptId",
            "scenarioId",
            "modelOutput",
            "safeOutput",
            "score",
            "status",
            "riskEvents",
            "retrievedDocs",
            "toolCalls",
            "createdAt",
        ]


class ReplaySerializer(serializers.ModelSerializer):
    attemptId = serializers.UUIDField(source="id")
    scenarioId = serializers.CharField(source="scenario_id")
    riskEvents = RiskEventSerializer(source="risk_events", many=True)
    repairAdvice = serializers.JSONField(source="repair_advice")

    class Meta:
        model = Attempt
        fields = ["attemptId", "scenarioId", "timeline", "riskEvents", "repairAdvice", "score", "status"]
