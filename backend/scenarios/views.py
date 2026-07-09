from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Attempt, Scenario, ScenarioDocument
from .serializers import AttemptSerializer, ReplaySerializer, ScenarioDetailSerializer, ScenarioDocumentSerializer, ScenarioListSerializer
from .services.orchestrator import run_attempt


@extend_schema(responses=ScenarioListSerializer(many=True))
@api_view(["GET"])
def scenario_list(request):
    scenarios = Scenario.objects.filter(is_active=True).select_related("default_defenses")
    return Response(ScenarioListSerializer(scenarios, many=True).data)


@extend_schema(responses=ScenarioDetailSerializer)
@api_view(["GET"])
def scenario_detail(request, scenario_id):
    scenario = get_object_or_404(Scenario.objects.select_related("default_defenses"), id=scenario_id, is_active=True)
    return Response(ScenarioDetailSerializer(scenario).data)


@extend_schema(methods=["GET"], responses=AttemptSerializer(many=True))
@extend_schema(
    methods=["POST"],
    request=inline_serializer(
        name="AttemptRequest",
        fields={
            "sessionId": serializers.CharField(required=False),
            "message": serializers.CharField(required=False),
            "messages": serializers.ListField(child=serializers.DictField(), required=False),
            "schema": serializers.JSONField(required=False),
            "documents": serializers.ListField(child=serializers.DictField(), required=False),
            "defenseOverrides": serializers.JSONField(required=False),
            "toolCalls": serializers.ListField(child=serializers.DictField(), required=False),
        },
    ),
    responses=AttemptSerializer,
)
@api_view(["GET", "POST"])
def scenario_attempts(request, scenario_id):
    scenario = get_object_or_404(Scenario.objects.select_related("default_defenses"), id=scenario_id, is_active=True)
    if request.method == "GET":
        session_id = request.query_params.get("sessionId", "demo-session")
        attempts = Attempt.objects.filter(scenario=scenario, session_id=session_id).prefetch_related("risk_events")[:20]
        return Response(AttemptSerializer(attempts, many=True).data)

    attempt = run_attempt(scenario, request.data)
    return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


@extend_schema(responses=ReplaySerializer)
@api_view(["GET"])
def attempt_replay(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.prefetch_related("risk_events"), id=attempt_id)
    return Response(ReplaySerializer(attempt).data)


@extend_schema(request=ScenarioDocumentSerializer, responses=ScenarioDocumentSerializer)
@api_view(["POST"])
def rag_documents(request, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id, category="indirect_prompt_injection")
    serializer = ScenarioDocumentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    document = serializer.save(scenario=scenario, is_poisoned=False, metadata={"source": "teacher-added"})
    return Response(ScenarioDocumentSerializer(document).data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=inline_serializer(name="ToolConfirmationRequest", fields={"decision": serializers.CharField(required=False)}),
    responses=inline_serializer(
        name="ToolConfirmationResponse",
        fields={
            "attemptId": serializers.UUIDField(),
            "status": serializers.CharField(),
            "timeline": serializers.JSONField(),
        },
    ),
)
@api_view(["POST"])
def confirm_tool_call(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    attempt.status = Attempt.Status.COMPLETED
    attempt.timeline.append({"phase": "human_confirmation", "data": {"decision": request.data.get("decision", "approved")}})
    attempt.save(update_fields=["status", "timeline"])
    return Response({"attemptId": attempt.id, "status": attempt.status, "timeline": attempt.timeline})
