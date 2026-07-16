// The rubric, typed for the browser — but NOT a second copy of it.
//
// INV-1 (one rubric, one source): the data below is imported from the evaluator's rubric.yaml at
// build time via the yamlPlugin in vite.config.ts. Nothing here hardcodes anchors, bands, or
// controls. parseRubric() validates the raw shape at the boundary so the rest of the app can rely
// on the typed structure. This mirrors evaluator/src/agent_evaluator/rubric.py.
import rawRubric from "../../../evaluator/src/agent_evaluator/rubric.yaml";

// Control levels, lowest to highest — used to order bands and apply override floors.
export const LEVEL_ORDER = ["C1", "C2", "C3", "C4"] as const;
export type Level = (typeof LEVEL_ORDER)[number];

export interface Dimension {
  key: string;
  label: string;
  question: string;
  /** Score (1..5) → anchor description. */
  anchors: Record<number, string>;
}

export interface Band {
  level: Level;
  name: string;
  min: number;
  max: number;
  summary: string;
}

export interface Override {
  dimension: string;
  atLeast: number;
  floor: Level;
  reason: string;
}

export interface Rubric {
  version: number;
  title: string;
  scaleMin: number;
  scaleMax: number;
  dimensions: Dimension[];
  bands: Band[];
  overrides: Override[];
  controls: Record<string, string[]>;
}

// --- boundary validation: unknown → typed, or throw --------------------------
function asRecord(v: unknown, ctx: string): Record<string, unknown> {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new Error(`rubric: expected an object at ${ctx}`);
  }
  return v as Record<string, unknown>;
}

function asArray(v: unknown, ctx: string): unknown[] {
  if (!Array.isArray(v)) throw new Error(`rubric: expected an array at ${ctx}`);
  return v;
}

function asString(v: unknown, ctx: string): string {
  if (typeof v !== "string") throw new Error(`rubric: expected a string at ${ctx}`);
  return v;
}

function asInt(v: unknown, ctx: string): number {
  if (typeof v !== "number" || !Number.isInteger(v)) {
    throw new Error(`rubric: expected an integer at ${ctx}`);
  }
  return v;
}

function asLevel(v: unknown, ctx: string): Level {
  const s = asString(v, ctx);
  if (!(LEVEL_ORDER as readonly string[]).includes(s)) {
    throw new Error(`rubric: '${s}' at ${ctx} is not a control level (${LEVEL_ORDER.join(", ")})`);
  }
  return s as Level;
}

function parseRubric(raw: unknown): Rubric {
  const root = asRecord(raw, "root");
  const scale = asRecord(root.scale, "scale");
  const agg = asRecord(root.aggregation, "aggregation");

  const dimensions: Dimension[] = asArray(root.dimensions, "dimensions").map((d, i) => {
    const dim = asRecord(d, `dimensions[${i}]`);
    const rawAnchors = asRecord(dim.anchors, `dimensions[${i}].anchors`);
    const anchors: Record<number, string> = {};
    for (const [k, val] of Object.entries(rawAnchors)) {
      anchors[Number(k)] = asString(val, `dimensions[${i}].anchors[${k}]`);
    }
    return {
      key: asString(dim.key, `dimensions[${i}].key`),
      label: asString(dim.label, `dimensions[${i}].label`),
      question: asString(dim.question, `dimensions[${i}].question`),
      anchors,
    };
  });

  const bands: Band[] = asArray(agg.bands, "aggregation.bands").map((b, i) => {
    const band = asRecord(b, `bands[${i}]`);
    return {
      level: asLevel(band.level, `bands[${i}].level`),
      name: asString(band.name, `bands[${i}].name`),
      min: asInt(band.min, `bands[${i}].min`),
      max: asInt(band.max, `bands[${i}].max`),
      summary: asString(band.summary, `bands[${i}].summary`),
    };
  });

  const overrides: Override[] = asArray(agg.overrides ?? [], "aggregation.overrides").map((o, i) => {
    const ov = asRecord(o, `overrides[${i}]`);
    return {
      dimension: asString(ov.dimension, `overrides[${i}].dimension`),
      atLeast: asInt(ov.at_least, `overrides[${i}].at_least`),
      floor: asLevel(ov.floor, `overrides[${i}].floor`),
      reason: asString(ov.reason, `overrides[${i}].reason`),
    };
  });

  const controls: Record<string, string[]> = {};
  for (const [level, items] of Object.entries(asRecord(root.controls, "controls"))) {
    controls[level] = asArray(items, `controls.${level}`).map((it, i) =>
      asString(it, `controls.${level}[${i}]`),
    );
  }

  return {
    version: asInt(root.version, "version"),
    title: asString(root.title, "title"),
    scaleMin: asInt(scale.min, "scale.min"),
    scaleMax: asInt(scale.max, "scale.max"),
    dimensions,
    bands,
    overrides,
    controls,
  };
}

/** The parsed, validated rubric — the single source of truth, read from rubric.yaml. */
export const rubric: Rubric = parseRubric(rawRubric);

export function bandForTotal(total: number, r: Rubric = rubric): Band {
  const band = r.bands.find((b) => b.min <= total && total <= b.max);
  if (!band) throw new Error(`total ${total} is outside every band range`);
  return band;
}

export function bandByLevel(level: Level, r: Rubric = rubric): Band {
  const band = r.bands.find((b) => b.level === level);
  if (!band) throw new Error(`no band with level ${level}`);
  return band;
}
