# DORA — IKT-Risiko-Checkliste für KI-Agenten

Eine Arbeits-Checkliste, die einen KI-Agenten aus der Perspektive des **IKT-Risikomanagements** nach
dem Digital Operational Resilience Act (DORA, Verordnung (EU) 2022/2554) betrachtet. Ein Agent —
besonders einer, der eine externe LLM-API aufruft — ist ein IKT-Asset und häufig eine
IKT-Drittdienstleister-Abhängigkeit; DORAs Resilienz-Disziplin gilt für ihn wie für jedes andere.

> **Dies ist ein Praktiker-Werkzeugkasten, keine Rechtsberatung.** DORA gilt für definierte
> Finanzunternehmen und unterliegt der Proportionalität. Ob eine konkrete Pflicht Sie bindet und wie,
> hängt von Unternehmenstyp und Ausgestaltung ab. Verstehen Sie die Artikelverweise als **indikative
> Hinweise, die gegen den aktuellen Rechtstext** und die einschlägigen RTS/ITS zu prüfen sind.
> Englische Fassung: [`dora-ict-risk-checklist.en.md`](dora-ict-risk-checklist.en.md).

Tragen Sie in **Status** ein: ✓ (erledigt), ✗ (offen) oder n/z.

## 1. IKT-Risikomanagement und Inventar

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 1.1 | Der Agent ist im **IKT-Asset-Inventar** erfasst und der unterstützten Geschäftsfunktion zugeordnet (IKT-Risikomanagement-Rahmen, Art. 5–6 — prüfen). | Inventareintrag | IT-Betrieb | ☐ |
| 1.2 | Seine **Abhängigkeiten** sind dokumentiert — Modelle, Datenspeicher, externe APIs, Orchestrierung. | Architektur / Abhängigkeitskarte | KI-Team | ☐ |
| 1.3 | Der Agent ist einer **Kritikalität / Toleranzschwelle** für die betroffene Funktion zugeordnet. | Business-Impact-Nachweis | Business (1st Line) | ☐ |
| 1.4 | **Schutz- und Präventionskontrollen** (Zugriff, Trennung, minimale Rechte am Aktionsraum) sind umgesetzt (Art. 9 — prüfen). | Kontroll-Design | KI-Team | ☐ |

## 2. Erkennung und Überwachung

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 2.1 | Anomales Agentenverhalten wird durch Monitoring und Schwellenwerte **erkannt** (Art. 10 — prüfen). Siehe [KPI-Katalog](../05-monitoring/kpi-catalog.md). | Monitoring-Konfiguration | IT-Betrieb | ☐ |
| 2.2 | Der Agent erzeugt einen **Audit-Trail**, der für Erkennung und Forensik ausreicht. Siehe [Logging-Anforderungen](../05-monitoring/logging-requirements.md). | Log-Beispiel | KI-Team | ☐ |

## 3. Reaktion, Wiederherstellung und Resilienztests

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 3.1 | **Ausfallszenarien** sind definiert und geübt: Modell/API nicht verfügbar, verschlechterte Ausgabe, Timeout, Rate-Limit, falsche-aber-überzeugte Ausgabe (Reaktion & Wiederherstellung, Art. 11 — prüfen). | Szenario-Playbook | KI-Team | ☐ |
| 3.2 | Ein **Fallback** bei Anbieter- oder Modellausfall ist definiert (graceful degradation, Halten in Warteschlange oder Übergabe an Menschen). | Design-Dokument | KI-Team | ☐ |
| 3.3 | **Backup und Wiederherstellung** von Zustand und Konfiguration des Agenten sind definiert und getestet (Art. 12 — prüfen). | Backup-Testnachweis | IT-Betrieb | ☐ |
| 3.4 | Der Agent ist in **Resilienztests** einbezogen, angemessen zu seiner Kritikalität (Testen der digitalen operationalen Resilienz, Art. 24–27 — prüfen). | Testplan/-ergebnisse | IT-Betrieb | ☐ |

## 4. IKT-Drittparteienrisiko — externe Modell- und API-Anbieter

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 4.1 | Ein **externer LLM-/API-Anbieter** ist als IKT-Drittparteienvereinbarung im Informationsregister erfasst (IKT-Drittparteienrisiko, Art. 28 — prüfen). | Drittparteienregister | Einkauf / Risiko | ☐ |
| 4.2 | Der **Vertrag** deckt die von DORA erwarteten Bestimmungen ab — Zugang, Audit, Weiterverlagerung, Service-Level, Kündigung, Zusammenarbeit bei Vorfällen, Datenort (Art. 30 — prüfen). | Vertragsklauseln | Recht / Einkauf | ☐ |
| 4.3 | **Konzentrations- und Exit-Risiko** ist bewertet — was passiert, wenn dieser Anbieter ausfällt oder ersetzt werden muss. | Exit-Plan | Risiko (2nd Line) | ☐ |
| 4.4 | An den Anbieter gesendete Daten sind **klassifiziert und minimiert**; der Umgang mit personenbezogenen oder besonderen Daten ist dokumentiert. | Datenfluss-Nachweis | KI-Team | ☐ |

## 5. Behandlung und Meldung von Vorfällen

| # | Kriterium | Nachweis | Verantwortlich | Status |
|:-:|-----------|----------|----------------|:------:|
| 5.1 | Ein **Vorfallmanagement-Prozess** deckt Agenten-Vorfälle ab — Erkennung, Behandlung, Eskalation (Art. 17 — prüfen). | Vorfallprozess | IT-Betrieb | ☐ |
| 5.2 | Agenten-Vorfälle werden gegen Ihre Kriterien für **schwerwiegende IKT-Vorfälle klassifiziert** (Art. 18 — prüfen). | Klassifizierungsnachweis | Risiko (2nd Line) | ☐ |
| 5.3 | **Meldewege** für schwerwiegende Vorfälle sind bekannt und geübt (Art. 19 — prüfen). | Eskalations-/Meldeplan | Risiko (2nd Line) | ☐ |

---

*Die Artikelverweise sind indikativ und gegen die aktuelle Fassung der Verordnung (EU) 2022/2554
sowie die einschlägigen RTS/ITS zu prüfen. Diese Checkliste stellt keine Konformität her.*
