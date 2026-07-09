from django.contrib import admin

from .models import Attempt, DefenseProfile, RiskEvent, Scenario, ScenarioDocument


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "difficulty", "is_active")
    search_fields = ("id", "title", "category")


@admin.register(DefenseProfile)
class DefenseProfileAdmin(admin.ModelAdmin):
    list_display = ("scenario", "input_moderation", "prompt_injection_detection", "encoding_normalization", "output_moderation")


@admin.register(ScenarioDocument)
class ScenarioDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "scenario", "is_poisoned")
    search_fields = ("title", "content")


class RiskEventInline(admin.TabularInline):
    model = RiskEvent
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "scenario", "session_id", "score", "status", "created_at")
    inlines = [RiskEventInline]


@admin.register(RiskEvent)
class RiskEventAdmin(admin.ModelAdmin):
    list_display = ("type", "severity", "source", "action", "created_at")
