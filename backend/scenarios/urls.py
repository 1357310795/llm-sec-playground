from django.urls import path

from . import views

urlpatterns = [
    path("scenarios/", views.scenario_list, name="scenario-list"),
    path("scenarios/<slug:scenario_id>/", views.scenario_detail, name="scenario-detail"),
    path("scenarios/<slug:scenario_id>/attempts/", views.scenario_attempts, name="scenario-attempts"),
    path("scenarios/<slug:scenario_id>/documents/", views.rag_documents, name="rag-documents"),
    path("attempts/<uuid:attempt_id>/replay/", views.attempt_replay, name="attempt-replay"),
    path("attempts/<uuid:attempt_id>/confirmations/", views.confirm_tool_call, name="tool-confirmation"),
]
