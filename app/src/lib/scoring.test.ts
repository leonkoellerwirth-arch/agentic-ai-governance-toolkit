// Parity checks for the TypeScript scorer against the three fictional example use-cases shipped in
// evaluator/examples/. The scores below are transcribed from those files; the expected bands are
// what `agent-eval score` produces. If the TS port drifts from risk_score.py, these fail.
import { describe, expect, it } from "vitest";
import { scoreAgent, type AgentAssessment } from "./scoring";

// Source: evaluator/examples/usecase-01-internal-knowledge-assistant.yaml
const INTERNAL_KNOWLEDGE: AgentAssessment = {
  name: "Internal knowledge assistant",
  scores: {
    autonomy: 1,
    action_space: 1,
    reversibility: 1,
    data_sensitivity: 2,
    explainability: 3,
    blast_radius: 2,
  },
};

// Source: evaluator/examples/usecase-02-customer-servicing-agent.yaml
const CUSTOMER_SERVICING: AgentAssessment = {
  name: "Customer-servicing agent",
  scores: {
    autonomy: 3,
    action_space: 3,
    reversibility: 3,
    data_sensitivity: 3,
    explainability: 3,
    blast_radius: 3,
  },
};

// Source: evaluator/examples/usecase-03-payments-operations-agent.yaml
const PAYMENTS_OPERATIONS: AgentAssessment = {
  name: "Payments operations agent",
  scores: {
    autonomy: 3,
    action_space: 5,
    reversibility: 4,
    data_sensitivity: 3,
    explainability: 3,
    blast_radius: 3,
  },
};

describe("scoreAgent (parity with risk_score.py)", () => {
  it("scores the internal knowledge assistant as C1 with no override", () => {
    const r = scoreAgent(INTERNAL_KNOWLEDGE);
    expect(r.total).toBe(10);
    expect(r.baseLevel).toBe("C1");
    expect(r.level).toBe("C1");
    expect(r.appliedOverrides).toHaveLength(0);
  });

  it("scores the customer-servicing agent as C3 with no override", () => {
    const r = scoreAgent(CUSTOMER_SERVICING);
    expect(r.total).toBe(18);
    expect(r.baseLevel).toBe("C3");
    expect(r.level).toBe("C3");
    expect(r.appliedOverrides).toHaveLength(0);
  });

  it("raises the payments agent from C3 to C4 via the action_space override", () => {
    const r = scoreAgent(PAYMENTS_OPERATIONS);
    expect(r.total).toBe(21);
    expect(r.baseLevel).toBe("C3");
    expect(r.level).toBe("C4");
    expect(r.appliedOverrides.map((o) => o.dimension)).toEqual(["action_space"]);
    expect(r.rationale).toContain("raises the required control intensity to C4");
    expect(r.controls.length).toBeGreaterThan(0);
  });

  it("rejects incomplete or out-of-range score sets", () => {
    expect(() => scoreAgent({ name: "x", scores: { autonomy: 1 } })).toThrow(/missing scores/);
    expect(() =>
      scoreAgent({ ...PAYMENTS_OPERATIONS, scores: { ...PAYMENTS_OPERATIONS.scores, autonomy: 9 } }),
    ).toThrow(/between 1 and 5/);
  });
});
