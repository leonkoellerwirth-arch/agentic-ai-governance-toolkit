import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { rubric } from "@/lib/rubric";
import { scoreAgent, type RiskResult } from "@/lib/scoring";
import { PRESETS } from "./presets";
import { DimensionStep } from "./DimensionStep";
import { ResultCard } from "./ResultCard";

type Scores = Record<string, number>;

export function AssessmentPage() {
  const { t } = useTranslation("common");
  const dims = rubric.dimensions;
  const maxTotal = dims.length * rubric.scaleMax;

  const [scores, setScores] = useState<Scores>({});
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<RiskResult | null>(null);

  const runningTotal = useMemo(
    () => Object.values(scores).reduce((sum, v) => sum + v, 0),
    [scores],
  );

  const current = dims[step];
  const currentAnswered = current !== undefined && scores[current.key] !== undefined;
  const isLastStep = step === dims.length - 1;
  const allAnswered = dims.every((d) => scores[d.key] !== undefined);

  function select(score: number) {
    if (!current) return;
    setScores((prev) => ({ ...prev, [current.key]: score }));
  }

  function next() {
    if (!isLastStep) {
      setStep(step + 1);
    } else if (allAnswered) {
      setResult(scoreAgent({ name: "Assessment", scores }));
    }
  }

  function loadPreset(key: string) {
    const preset = PRESETS.find((p) => p.key === key);
    if (!preset) return;
    setScores({ ...preset.assessment.scores });
    setResult(scoreAgent(preset.assessment));
  }

  function reset() {
    setScores({});
    setStep(0);
    setResult(null);
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-8 px-4 py-10">
      <header className="flex flex-col gap-3">
        <p className="text-neutral-700">{t("lead")}</p>
        <p className="text-xs uppercase tracking-wide text-neutral-400">{t("levelScale")}</p>
        <label className="mt-2 flex flex-col gap-1 text-sm text-neutral-500 sm:flex-row sm:items-center sm:gap-2">
          {t("presets.label")}
          <select
            className="rounded-md border border-neutral-300 px-2 py-1 text-neutral-800"
            value=""
            onChange={(e) => loadPreset(e.target.value)}
          >
            <option value="" disabled>
              {t("presets.placeholder")}
            </option>
            {PRESETS.map((p) => (
              <option key={p.key} value={p.key}>
                {p.assessment.name}
              </option>
            ))}
          </select>
        </label>
      </header>

      {result ? (
        <>
          <ResultCard result={result} maxTotal={maxTotal} />
          <button
            type="button"
            onClick={reset}
            className="self-start rounded-full bg-neutral-900 px-5 py-2 text-sm text-white"
          >
            {t("nav.startOver")}
          </button>
        </>
      ) : (
        current && (
          <section className="flex flex-col gap-6">
            <div className="flex items-center justify-between text-xs text-neutral-400">
              <span>{t("assessment.step", { current: step + 1, total: dims.length })}</span>
              <span className="tabular-nums">
                {t("assessment.runningTotal", { total: runningTotal, max: maxTotal })}
              </span>
            </div>

            <DimensionStep
              dimension={current}
              scaleMin={rubric.scaleMin}
              scaleMax={rubric.scaleMax}
              value={scores[current.key]}
              onSelect={select}
            />

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStep(Math.max(0, step - 1))}
                disabled={step === 0}
                className="rounded-full px-5 py-2 text-sm text-neutral-600 disabled:opacity-40"
              >
                {t("nav.back")}
              </button>
              <button
                type="button"
                onClick={next}
                disabled={!currentAnswered}
                className="rounded-full bg-neutral-900 px-5 py-2 text-sm text-white disabled:opacity-40"
              >
                {isLastStep ? t("nav.seeResult") : t("nav.next")}
              </button>
            </div>

            {!currentAnswered && (
              <p className="text-center text-xs text-neutral-400">{t("assessment.answeredHint")}</p>
            )}
          </section>
        )
      )}
    </div>
  );
}
