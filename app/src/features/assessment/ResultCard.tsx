import { useTranslation } from "react-i18next";
import type { RiskResult } from "@/lib/scoring";

interface Props {
  result: RiskResult;
  maxTotal: number;
}

/** The outcome, written for a non-technical reader: the control level and its plain-language
 *  meaning up top, then any overrides, the minimum safeguards, and the full rationale. */
export function ResultCard({ result, maxTotal }: Props) {
  const { t } = useTranslation("common");
  const overridden = result.level !== result.baseLevel;

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-neutral-200 pb-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-neutral-400">{t("result.heading")}</p>
          <p className="text-3xl font-semibold">
            {result.level} · {result.levelName}
          </p>
        </div>
        <p className="text-2xl tabular-nums text-neutral-500">
          {t("result.total", { total: result.total, max: maxTotal })}
        </p>
      </div>

      <p className="text-neutral-700">{result.summary}</p>

      {overridden && (
        <p className="text-sm text-neutral-500">{t("result.baseWas", { level: result.baseLevel })}</p>
      )}

      {result.appliedOverrides.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-semibold">{t("result.overrides")}</h3>
          <ul className="flex flex-col gap-1 pl-5 text-sm text-neutral-600 [list-style:disc]">
            {result.appliedOverrides.map((o) => (
              <li key={o.dimension}>
                {o.dimension.replace(/_/g, " ")} → {o.floor}: {o.reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-col gap-2">
        <h3 className="text-sm font-semibold">{t("result.controls")}</h3>
        <ul className="flex flex-col gap-1 pl-5 text-sm text-neutral-600 [list-style:disc]">
          {result.controls.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="text-sm font-semibold">{t("result.rationale")}</h3>
        <p className="text-sm text-neutral-600">{result.rationale}</p>
      </div>
    </section>
  );
}
