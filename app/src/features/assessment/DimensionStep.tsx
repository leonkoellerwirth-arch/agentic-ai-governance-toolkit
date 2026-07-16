import type { Dimension } from "@/lib/rubric";

interface Props {
  dimension: Dimension;
  scaleMin: number;
  scaleMax: number;
  value: number | undefined;
  onSelect: (score: number) => void;
}

/** One dimension of the assessment: its plain-language question and all 1..5 anchor statements as
 *  selectable rows. Deliberately shows every anchor so a non-expert can read what each score means. */
export function DimensionStep({ dimension, scaleMin, scaleMax, value, onSelect }: Props) {
  const scores: number[] = [];
  for (let s = scaleMin; s <= scaleMax; s++) scores.push(s);

  return (
    <fieldset className="flex flex-col gap-4">
      <legend className="text-xl font-semibold">{dimension.label}</legend>
      <p className="text-neutral-600">{dimension.question}</p>
      <div className="flex flex-col gap-2">
        {scores.map((s) => {
          const selected = value === s;
          return (
            <button
              key={s}
              type="button"
              aria-pressed={selected}
              onClick={() => onSelect(s)}
              className={`flex items-start gap-3 rounded-lg border px-4 py-3 text-left text-sm transition ${
                selected
                  ? "border-neutral-900 bg-neutral-50"
                  : "border-neutral-200 hover:border-neutral-400"
              }`}
            >
              <span className="mt-0.5 font-mono text-xs text-neutral-400">{s}</span>
              <span>{dimension.anchors[s]}</span>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
