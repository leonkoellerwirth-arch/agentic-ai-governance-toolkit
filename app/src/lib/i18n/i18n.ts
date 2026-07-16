// Canonical i18n init — all catalogues bundled eagerly (zero network, offline from first paint).
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { DEFAULT_NAMESPACE, I18N_NAMESPACES } from "./namespaces";
import { DEFAULT_LANGUAGE, initialLanguage } from "./languages";

const catalogModules = import.meta.glob<{ default: Record<string, unknown> }>(
  "../../locales/**/*.json",
  { eager: true },
);

function buildBundledResources() {
  const res: Record<string, Record<string, Record<string, unknown>>> = {};
  for (const [p, mod] of Object.entries(catalogModules)) {
    const m = p.match(/\/locales\/([^/]+)\/([^/]+)\.json$/);
    if (!m) continue;
    const [, lang, ns] = m;
    if (!lang || !ns) continue;
    (res[lang] ??= {})[ns] = mod.default ?? {};
  }
  return res;
}

if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources: buildBundledResources(),
    lng: initialLanguage(),
    fallbackLng: DEFAULT_LANGUAGE,
    ns: [...I18N_NAMESPACES],
    defaultNS: DEFAULT_NAMESPACE,
    interpolation: { escapeValue: false },
    returnNull: false,
    returnEmptyString: false,
    react: { useSuspense: false },
  });
}

export default i18n;
