# EU AI Act — Checkliste für KI-Agenten

Eine Arbeits-Checkliste für Teams, die einen KI-Agenten in einer regulierten Organisation einführen.
Sie konzentriert sich auf die für **Agenten** wesentlichen Themen — Risikoklassifizierung,
Transparenz, menschliche Aufsicht und Logging-/Dokumentationspflichten — und verweist darauf, wo
diese in der KI-Verordnung (Verordnung (EU) 2024/1689) verortet sind.

> **Dies ist ein Praktiker-Werkzeugkasten, keine Rechtsberatung.** Ob und wie eine konkrete Pflicht
> gilt, hängt von der Risikoklasse des Systems, Ihrer Rolle (Anbieter, Betreiber, …) und dem
> Einzelfall ab. Verstehen Sie die Artikelverweise als **indikative Hinweise, die gegen den aktuellen
> Rechtstext zu prüfen sind** — nicht als Feststellung, dass eine Pflicht greift. Klären Sie dies mit
> qualifizierter Rechtsberatung und Ihrer Compliance-Funktion. Englische Fassung:
> [`eu-ai-act-agent-checklist.en.md`](eu-ai-act-agent-checklist.en.md).

Tragen Sie in **Status** ein: ✓ (erledigt), ✗ (offen) oder n/z. Vermerken Sie, wo der Nachweis liegt.

## 1. Klassifizierung — welche Art von KI-System ist das?

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 1.1 | Der Agent wurde gegen die **verbotenen Praktiken** geprüft und fällt nicht darunter (KI-VO, Art. 5 — prüfen). | Triage-Notiz | Risiko (2nd Line) | ☐ |
| 1.2 | Die **Risikoklasse** des Agenten wurde bestimmt (hochriskant nach Art. 6 / Anhang III, Transparenzrisiko oder minimal), mit Begründung. | Klassifizierung | Risiko (2nd Line) | ☐ |
| 1.3 | Ihre **Rolle** in der Wertschöpfungskette (Anbieter / Betreiber / Händler) ist bestimmt, da sich die Pflichten je Rolle unterscheiden. | Klassifizierung | Risiko (2nd Line) | ☐ |
| 1.4 | Baut der Agent auf einem **KI-Modell mit allgemeinem Verwendungszweck** auf, sind die zugehörigen Pflichten berücksichtigt (Art. 51–55 — prüfen). | Modell-Inventar | KI-Team | ☐ |

## 2. Transparenz

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 2.1 | Personen, die **mit dem Agenten interagieren**, werden — soweit erforderlich — darüber informiert, dass es sich um eine KI handelt (Transparenzpflichten, Art. 50 — prüfen). | UX-Text / Hinweis | KI-Team | ☐ |
| 2.2 | **KI-erzeugte oder manipulierte Inhalte** des Agenten werden, soweit erforderlich, gekennzeichnet. | Ausgabe-Kennzeichnung | KI-Team | ☐ |
| 2.3 | Betreiber erhalten die **Informationen und Anweisungen**, die sie für den korrekten Einsatz brauchen (Art. 13 bei Hochrisiko — prüfen). | Betriebsanleitung | Anbieter | ☐ |

## 3. Menschliche Aufsicht

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 3.1 | Die Autonomie des Agenten ist durch einen definierten **Aktionsraum** begrenzt; Aktionen außerhalb werden verweigert. | Design-Dokument | KI-Team | ☐ |
| 3.2 | **Menschliche Aufsicht** ist risikoangemessen mitgestaltet — ein Mensch kann prüfen, eingreifen und den Agenten stoppen (Art. 14 bei Hochrisiko — prüfen). | HITL-Design | KI-Team | ☐ |
| 3.3 | Für höhere Kontrollstufen (C3–C4) erfordern Aktionen im Geltungsbereich eine **ausdrückliche menschliche Freigabe/Ablehnung** bzw. Einzelfreigabe. | Kontroll-Design | Risiko (2nd Line) | ☐ |
| 3.4 | Ein **Not-Aus/Stopp**-Verfahren existiert und wurde getestet. | Runbook + Testnachweis | IT-Betrieb | ☐ |

## 4. Logging, Aufzeichnung und Dokumentation

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 4.1 | Der Agent führt einen **Audit-Trail** seiner Entscheidungen und Aktionen, der ausreicht, um das Geschehen zu rekonstruieren (Aufzeichnung, Art. 12 bei Hochrisiko — prüfen). Siehe [Logging-Anforderungen](../05-monitoring/logging-requirements.md). | Log-Beispiel | KI-Team | ☐ |
| 4.2 | Eine **technische Dokumentation** des Agenten, seiner Daten und Kontrollen wird gepflegt (Art. 11 / Anhang IV bei Hochrisiko — prüfen). | Techn. Doku | KI-Team | ☐ |
| 4.3 | **Daten-Governance** für Trainings-/Referenzdaten ist adressiert — Herkunft, Qualität, Umgang mit personenbezogenen Daten (Art. 10 bei Hochrisiko — prüfen). | Daten-Governance-Nachweis | KI-Team | ☐ |
| 4.4 | **Genauigkeit, Robustheit und Cybersicherheit** sind risikoangemessen getestet (Art. 15 bei Hochrisiko — prüfen). | Testnachweis | KI-Team | ☐ |

## 5. Governance rund um den Agenten

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 5.1 | Ein **Risikomanagement** deckt den Agenten über den Lebenszyklus ab (Art. 9 bei Hochrisiko — prüfen). | Risikobewertung | Risiko (2nd Line) | ☐ |
| 5.2 | Ein **verantwortlicher Owner** ist benannt und im Agenten-Register erfasst. | Registereintrag | Business (1st Line) | ☐ |
| 5.3 | **Re-Assessment** ist geplant und wird durch wesentliche Änderungen ausgelöst (Modell, Autonomie, Daten, Aktionsraum). | Re-Assessment-Plan | Risiko (2nd Line) | ☐ |

---

*Die Artikelverweise sind indikativ und gegen die aktuelle konsolidierte Fassung der Verordnung (EU)
2024/1689 sowie ihre Durchführungsrechtsakte zu prüfen. Diese Checkliste stellt keine Konformität her.*
