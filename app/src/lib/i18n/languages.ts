import i18n from "i18next";

// The toolkit's checklists ship EN/DE; the console mirrors that pair. English is the default
// because the repository's primary docs are English (BIBLE zone: public work sample).
export const LANGUAGES = ["en", "de"] as const;
export type LangCode = (typeof LANGUAGES)[number];

export const DEFAULT_LANGUAGE: LangCode = "en";
export const LANG_STORAGE_KEY = "governance-console:lang";

export function initialLanguage(): LangCode {
  const saved = typeof localStorage !== "undefined" ? localStorage.getItem(LANG_STORAGE_KEY) : null;
  return (LANGUAGES as readonly string[]).includes(saved ?? "") ? (saved as LangCode) : DEFAULT_LANGUAGE;
}

export function setLang(lang: LangCode): void {
  localStorage.setItem(LANG_STORAGE_KEY, lang);
  void i18n.changeLanguage(lang);
}
