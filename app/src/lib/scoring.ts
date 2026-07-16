// Control-intensity scoring — a faithful TypeScript port of
// evaluator/src/agent_evaluator/risk_score.py. The algorithm and rationale text are kept identical
// so the console and the `agent-eval score` CLI produce the same result for the same input.
import {
  bandByLevel,
  bandForTotal,
  LEVEL_ORDER,
  rubric as defaultRubric,
  type Band,
  type Level,
  type Rubric,
} from "./rubric";

export interface AgentAssessment {
  name: string;
  description?: string;
  /** Dimension key → score (1..5). */
  scores: Record<string, number>;
}

export interface AppliedOverride {
  dimension: string;
  floor: Level;
  reason: string;
}

export interface RiskResult {
  agentName: string;
  scores: Record<string, number>;
  total: number;
  baseLevel: Level;
  level: Level;
  levelName: string;
  summary: string;
  appliedOverrides: AppliedOverride[];
  controls: string[];
  rationale: string;
}

function dimensionKeys(r: Rubric): string[] {
  return r.dimensions.map((d) => d.key);
}

function validateScores(scores: Record<string, number>, r: Rubric): void {
  const expected = new Set(dimensionKeys(r));
  const got = new Set(Object.keys(scores));
  const missing = [...expected].filter((k) => !got.has(k)).sort();
  const unknown = [...got].filter((k) => !expected.has(k)).sort();
  if (missing.length) throw new Error(`missing scores for: ${missing.join(", ")}`);
  if (unknown.length) throw new Error(`unknown dimension(s): ${unknown.join(", ")}`);
  for (const key of dimensionKeys(r)) {
    const value = scores[key] as number;
    if (value < r.scaleMin || value > r.scaleMax) {
      throw new Error(
        `score for '${key}' is ${value}; must be between ${r.scaleMin} and ${r.scaleMax}`,
      );
    }
  }
}

function higherLevel(a: Level, b: Level): Level {
  return LEVEL_ORDER.indexOf(a) >= LEVEL_ORDER.indexOf(b) ? a : b;
}

export function scoreAgent(assessment: AgentAssessment, r: Rubric = defaultRubric): RiskResult {
  validateScores(assessment.scores, r);

  const total = dimensionKeys(r).reduce((sum, key) => sum + (assessment.scores[key] as number), 0);
  const baseBand = bandForTotal(total, r);

  // Overrides raise the floor; the final level is the highest of the base band and every floor.
  const applied: AppliedOverride[] = [];
  for (const override of r.overrides) {
    if ((assessment.scores[override.dimension] as number) >= override.atLeast) {
      applied.push({ dimension: override.dimension, floor: override.floor, reason: override.reason });
    }
  }

  const finalLevel = applied.reduce<Level>((lvl, o) => higherLevel(lvl, o.floor), baseBand.level);
  const finalBand = bandByLevel(finalLevel, r);

  return {
    agentName: assessment.name,
    scores: { ...assessment.scores },
    total,
    baseLevel: baseBand.level,
    level: finalBand.level,
    levelName: finalBand.name,
    summary: finalBand.summary,
    appliedOverrides: applied,
    controls: [...(r.controls[finalBand.level] ?? [])],
    rationale: buildRationale(total, baseBand, finalBand, applied, r),
  };
}

function buildRationale(
  total: number,
  base: Band,
  final: Band,
  applied: AppliedOverride[],
  r: Rubric,
): string {
  const maxTotal = r.dimensions.length * r.scaleMax;
  const parts = [`Total ${total}/${maxTotal} places this agent in ${base.level} (${base.name}).`];
  if (final.level !== base.level) {
    const drivers = applied
      .map((o) => `${o.dimension.replace(/_/g, " ")} (→ ${o.floor}): ${o.reason}`)
      .join("; ");
    parts.push(
      `An override raises the required control intensity to ${final.level} (${final.name}) — ${drivers}`,
    );
  }
  parts.push(final.summary);
  return parts.join(" ");
}
