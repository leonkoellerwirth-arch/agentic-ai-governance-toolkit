import { useTranslation } from "react-i18next";
import { LANGUAGES, setLang } from "./lib/i18n/languages";

export function App() {
  const { t, i18n } = useTranslation("common");
  return (
    <main className="min-h-dvh flex flex-col items-center justify-center gap-6 p-8 text-center">
      <h1 className="text-3xl font-semibold text-balance">{t("title")}</h1>
      <p className="max-w-prose text-neutral-500">{t("tagline")}</p>
      <div className="flex gap-2">
        {LANGUAGES.map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            className={`rounded-full px-4 py-2 text-sm ${
              i18n.language === l ? "bg-neutral-900 text-white" : "bg-neutral-100"
            }`}
          >
            {l.toUpperCase()}
          </button>
        ))}
      </div>
      <p className="max-w-prose text-xs text-neutral-400">{t("disclaimer")}</p>
    </main>
  );
}
