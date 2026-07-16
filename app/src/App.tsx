import { useTranslation } from "react-i18next";
import { LANGUAGES, setLang } from "./lib/i18n/languages";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { AssessmentPage } from "./features/assessment/AssessmentPage";

export function App() {
  const { t, i18n } = useTranslation("common");
  return (
    <div className="min-h-dvh bg-white text-neutral-900">
      <DisclaimerBanner />
      <header className="flex items-center justify-between border-b border-neutral-200 px-4 py-3">
        <h1 className="text-lg font-semibold">{t("title")}</h1>
        <div className="flex gap-1">
          {LANGUAGES.map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLang(l)}
              aria-pressed={i18n.language === l}
              className={`rounded-full px-3 py-1 text-xs ${
                i18n.language === l ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-600"
              }`}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>
      </header>
      <main>
        <AssessmentPage />
      </main>
    </div>
  );
}
