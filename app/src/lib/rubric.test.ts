// Structure checks on the rubric as imported from rubric.yaml. This is the browser-side analog of
// evaluator/tests/test_rubric_consistency.py: it fails if the single source of truth loses its
// expected shape, catching drift before it reaches the UI.
import { describe, expect, it } from "vitest";
import { LEVEL_ORDER, rubric } from "./rubric";

const EXPECTED_DIMENSIONS = [
  "autonomy",
  "action_space",
  "reversibility",
  "data_sensitivity",
  "explainability",
  "blast_radius",
];

describe("rubric (imported from rubric.yaml)", () => {
  it("has the six expected dimensions in order", () => {
    expect(rubric.dimensions.map((d) => d.key)).toEqual(EXPECTED_DIMENSIONS);
  });

  it("gives every dimension a full 1..5 anchor set with a question", () => {
    for (const d of rubric.dimensions) {
      expect(d.question.length).toBeGreaterThan(0);
      for (let score = rubric.scaleMin; score <= rubric.scaleMax; score++) {
        expect(typeof d.anchors[score]).toBe("string");
      }
    }
  });

  it("uses a 1..5 scale", () => {
    expect(rubric.scaleMin).toBe(1);
    expect(rubric.scaleMax).toBe(5);
  });

  it("has four bands C1..C4 that are contiguous and non-overlapping", () => {
    expect(rubric.bands.map((b) => b.level)).toEqual([...LEVEL_ORDER]);
    const sorted = [...rubric.bands].sort((a, b) => a.min - b.min);
    expect(sorted[0]?.min).toBe(rubric.dimensions.length * rubric.scaleMin); // 6
    expect(sorted[sorted.length - 1]?.max).toBe(rubric.dimensions.length * rubric.scaleMax); // 30
    for (let i = 1; i < sorted.length; i++) {
      expect(sorted[i]?.min).toBe((sorted[i - 1]?.max ?? 0) + 1);
    }
  });

  it("defines minimum controls for every band level", () => {
    for (const level of LEVEL_ORDER) {
      expect(rubric.controls[level]?.length ?? 0).toBeGreaterThan(0);
    }
  });

  it("only references known dimensions and levels in overrides", () => {
    const keys = new Set(rubric.dimensions.map((d) => d.key));
    for (const o of rubric.overrides) {
      expect(keys.has(o.dimension)).toBe(true);
      expect((LEVEL_ORDER as readonly string[]).includes(o.floor)).toBe(true);
    }
  });
});
