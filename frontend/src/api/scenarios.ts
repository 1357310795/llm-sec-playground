import { apiRequest } from './client';
import type { AttemptPayload, AttemptResult, Replay, Scenario } from '../types';

export function getScenarios() {
  return apiRequest<Scenario[]>('/scenarios/');
}

export function getScenario(id: string) {
  return apiRequest<Scenario>(`/scenarios/${id}/`);
}

export function submitAttempt(scenarioId: string, payload: AttemptPayload) {
  return apiRequest<AttemptResult>(`/scenarios/${scenarioId}/attempts/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getReplay(attemptId: string) {
  return apiRequest<Replay>(`/attempts/${attemptId}/replay/`);
}
