import { useTranslation } from "react-i18next";

/** Persistent, non-dismissable governance disclaimer (INV-3). Modeled on DISCLAIMER.md; shown on
 *  every screen so the "reference pattern, not compliance" framing is never lost. */
export function DisclaimerBanner() {
  const { t } = useTranslation("common");
  return (
    <p role="note" className="border-b border-neutral-200 bg-neutral-50 px-4 py-2 text-center text-xs text-neutral-500">
      {t("disclaimer")}
    </p>
  );
}
