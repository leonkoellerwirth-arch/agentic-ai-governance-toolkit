// The three fictional example use-cases, offered as one-click presets. They are imported straight
// from evaluator/examples/*.yaml (INV-2: no hand-copied names or scores) and validated into the
// AgentAssessment shape the scorer expects.
import type { AgentAssessment } from "@/lib/scoring";
import uc1 from "../../../../evaluator/examples/usecase-01-internal-knowledge-assistant.yaml";
import uc2 from "../../../../evaluator/examples/usecase-02-customer-servicing-agent.yaml";
import uc3 from "../../../../evaluator/examples/usecase-03-payments-operations-agent.yaml";

export interface Preset {
  key: string;
  assessment: AgentAssessment;
}

function toAssessment(raw: unknown, key: string): AgentAssessment {
  if (typeof raw !== "object" || raw === null) throw new Error(`preset ${key}: expected an object`);
  const o = raw as Record<string, unknown>;
  if (typeof o.scores !== "object" || o.scores === null) {
    throw new Error(`preset ${key}: missing scores`);
  }
  const scores: Record<string, number> = {};
  for (const [dim, value] of Object.entries(o.scores as Record<string, unknown>)) {
    if (typeof value !== "number") throw new Error(`preset ${key}: score '${dim}' is not a number`);
    scores[dim] = value;
  }
  return {
    name: typeof o.name === "string" ? o.name : key,
    description: typeof o.description === "string" ? o.description : undefined,
    scores,
  };
}

export const PRESETS: Preset[] = [
  { key: "internal-knowledge", assessment: toAssessment(uc1, "internal-knowledge") },
  { key: "customer-servicing", assessment: toAssessment(uc2, "customer-servicing") },
  { key: "payments-operations", assessment: toAssessment(uc3, "payments-operations") },
];
