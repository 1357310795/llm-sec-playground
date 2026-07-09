export type DefenseProfile = {
  inputModeration: boolean;
  promptInjectionDetection: boolean;
  encodingNormalization: boolean;
  instructionDataSeparation: boolean;
  outputModeration: boolean;
  toolPolicyEnforcement: boolean;
  humanConfirmationRequired: boolean;
  rateLimit: boolean;
};

export type Scenario = {
  id: string;
  title: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  summary: string;
  chapterRefs: string[];
  learningGoals: string[];
  allowedInputs: Array<'chat' | 'file' | 'url' | 'schema' | 'image'>;
  trainingTargets: string[];
  defaultDefenses: DefenseProfile;
  successConditions?: Array<Record<string, unknown>>;
  hints?: string[];
};

export type RiskEvent = {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  message: string;
  span?: string;
  action: string;
  metadata?: Record<string, unknown>;
};

export type AttemptResult = {
  attemptId: string;
  scenarioId: string;
  modelOutput: string;
  safeOutput: string;
  score: number;
  status: string;
  riskEvents: RiskEvent[];
  retrievedDocs: Array<Record<string, unknown>>;
  toolCalls: Array<Record<string, unknown>>;
  createdAt: string;
};

export type AttemptPayload = {
  sessionId: string;
  message: string;
  messages: Array<Record<string, string>>;
  defenses: DefenseProfile;
  schema?: unknown;
  documents: Array<{ title: string; content: string }>;
};

export type Replay = {
  attemptId: string;
  scenarioId: string;
  timeline: Array<Record<string, unknown>>;
  riskEvents: RiskEvent[];
  repairAdvice: string[];
  score: number;
  status: string;
};
