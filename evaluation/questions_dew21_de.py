# DEW21-provided German evaluation questions
# Ground truths derived from: AGB Strom §22, Anhang SCHUFA, Anhang Creditreform

QUESTIONS_DEW21_DE = [

    # ── 1. Allgemeine Rechtsauskünfte ────────────────────────────────────────

    {
        "question": "Darf ich diese Kundendaten weitergeben?",
        "ground_truth": (
            "DEW21 darf Kundendaten auf Basis von Art. 6 Abs. 1 lit. b und f DSGVO an "
            "SCHUFA und Creditreform zur Bonitätsprüfung und zum Schutz vor Zahlungsausfall "
            "übermitteln. Eine Weitergabe ist nur zulässig, wenn ein berechtigtes Interesse "
            "besteht und dieses die Interessen des Kunden überwiegt. Eine Übermittlung in "
            "Drittländer findet nicht statt (§22.4e, §22.6 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "Welche Daten darf ich für diesen Prozess speichern?",
        "ground_truth": (
            "DEW21 darf folgende Datenkategorien speichern: Kundenkontaktdaten (Name, Adresse, "
            "E-Mail, Telefon), Lieferadressdaten (Zählernummer, Marktlokations-ID), "
            "Verbrauchsdaten, Informationen zur Lieferdauer, Abrechnungsdaten (Bankverbindung) "
            "sowie Daten zum Zahlungsverhalten. Die Verarbeitung muss auf einer Rechtsgrundlage "
            "nach Art. 6 DSGVO basieren (§22.3 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "Muss ich eine Einwilligung einholen?",
        "ground_truth": (
            "Eine Einwilligung (Art. 6 Abs. 1 lit. a DSGVO) ist nur für das Telefonmarketing "
            "erforderlich. Für die Vertragserfüllung, gesetzliche Pflichten und berechtigte "
            "Interessen ist keine Einwilligung notwendig — es gelten Art. 6 Abs. 1 lit. b, c "
            "und f DSGVO. Die Übermittlung an SCHUFA und Creditreform erfolgt auf Basis des "
            "berechtigten Interesses (Art. 6 Abs. 1 lit. f DSGVO), nicht auf Basis einer "
            "Einwilligung (§22.4 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "Welche gesetzlichen Vorgaben gelten für Fernwärmeverträge?",
        "ground_truth": (
            "Die verfügbaren DEW21-Dokumente behandeln ausschließlich Strom- und Erdgaslieferverträge. "
            "Fernwärmeverträge sind in der aktuellen Dokumentenbasis nicht abgedeckt und erfordern "
            "separate Regelwerke und gesetzliche Grundlagen."
        ),
        "document": None,
    },
    {
        "question": "Welche Informationspflichten haben Energieunternehmen gegenüber Kund:innen?",
        "ground_truth": (
            "DEW21 muss Kunden informieren über: Preisänderungen mindestens 6 Wochen vor "
            "Inkrafttreten (§9.13); Vertragsänderungen mindestens 6 Wochen im Voraus (§21.2); "
            "das Sonderkündigungsrecht bei Preis- oder Vertragsänderungen; den zuständigen "
            "Netzbetreiber (§12); sowie Möglichkeiten zur außergerichtlichen Streitbeilegung "
            "durch die Schlichtungsstelle Energie (§23.1 AGB Strom)."
        ),
        "document": "strom",
    },
    {
        "question": "Welche rechtlichen Rahmenbedingungen gelten bei Sperrungen oder Mahnverfahren?",
        "ground_truth": (
            "Eine Unterbrechung der Stromlieferung ist zulässig, wenn der offene Betrag dem "
            "Doppelten der monatlichen Abschlagszahlung oder mindestens 100 Euro entspricht. "
            "Der Kunde muss mindestens 4 Wochen vorher informiert werden. Inkasso- und "
            "Anwaltskosten können dem Kunden gemäß §288 BGB in Rechnung gestellt werden. "
            "Die Mindestbetragsschwellen des §19 Abs. 2 StromGVV müssen eingehalten werden "
            "(§7.5 AGB Strom)."
        ),
        "document": "strom",
    },
    {
        "question": "Was muss im Schriftverkehr rechtlich zwingend enthalten sein?",
        "ground_truth": (
            "Schriftliche Mitteilungen von DEW21 müssen enthalten: das geplante Inkrafttreten "
            "und die Begründung von Preis- oder Vertragsänderungen; den Hinweis auf das "
            "Sonderkündigungsrecht und die entsprechende Frist; bei Sperrandrohungen das "
            "geplante Unterbrechungsdatum mindestens 4 Wochen im Voraus. "
            "Kündigungsbestätigungen müssen das Vertragsendedatum benennen (§9.13, §18.1, "
            "§21.2 AGB Strom)."
        ),
        "document": "strom",
    },

    # ── 2. Datenschutz & DSGVO ───────────────────────────────────────────────

    {
        "question": "Wie lange dürfen wir diese Daten aufbewahren?",
        "ground_truth": (
            "Gemäß §22.7 AGB Strom werden personenbezogene Daten nur so lange gespeichert, "
            "wie es für den jeweiligen Zweck erforderlich ist. Daten für Direktmarketing "
            "werden spätestens 12 Monate nach Vertragsende gelöscht. SCHUFA speichert Daten "
            "standardmäßig 3 Jahre nach Erledigung. Creditreform speichert Daten zunächst "
            "4 Jahre und löscht sie nach Erledigung eines Vorgangs genau 3 Jahre danach."
        ),
        "document": None,
    },
    {
        "question": "Welche rechtlichen Risiken bestehen bei dieser Antwort an den Kunden?",
        "ground_truth": (
            "Die verfügbaren DEW21-Dokumente enthalten keine allgemeine Risikoabschätzung für "
            "individuelle Kundenantworten. Eine rechtliche Risikobewertung erfordert "
            "fallspezifische juristische Beratung, die über den Inhalt dieser "
            "Allgemeinen Geschäftsbedingungen hinausgeht."
        ),
        "document": None,
    },

    # ── 3. Juristische Entscheidungsunterstützung ────────────────────────────

    {
        "question": "Welche möglichen Szenarien gibt es in diesem Fall?",
        "ground_truth": (
            "Die verfügbaren Dokumente unterstützen keine offene Szenarienanalyse. "
            "Die AGB Strom regelt konkrete Szenarien wie Zahlungsverzug (§7.5), "
            "Lieferunterbrechung (§7.5), Preisstreitigkeiten (§10) und außerordentliche "
            "Kündigung (§18.2), jedoch ist eine allgemeine Szenarienübersicht vom "
            "jeweiligen Fallkontext abhängig."
        ),
        "document": "strom",
    },
    {
        "question": "Wie hoch ist das Risiko bei diesen Optionen?",
        "ground_truth": (
            "Eine Risikobewertung ist in den verfügbaren DEW21-Dokumenten nicht enthalten. "
            "Die Dokumente regeln vertragliche Pflichten und Rechtsgrundlagen, nehmen jedoch "
            "keine Einschätzung oder Gewichtung von Risiken einzelner Entscheidungsoptionen vor."
        ),
        "document": None,
    },
    {
        "question": "Was wäre der formal richtige nächste Schritt?",
        "ground_truth": (
            "Der formal richtige nächste Schritt hängt vom Sachverhalt ab. Bei Zahlungsverzug: "
            "Mahnung versenden, anschließend Sperrankündigung mit 4 Wochen Vorlauf (§7.5). "
            "Bei Preisänderungen: schriftliche Ankündigung mindestens 6 Wochen vorher mit "
            "Hinweis auf Sonderkündigungsrecht (§9.13). Bei Vertragsstreitigkeiten: Verweis "
            "auf die Schlichtungsstelle Energie (§23.1 AGB Strom)."
        ),
        "document": "strom",
    },

    # ── 4. Typische Kundenfragen ─────────────────────────────────────────────

    {
        "question": "Wieso werde ich in der Grundversorgung angemeldet, obwohl ich keinen Vertrag abgeschlossen habe?",
        "ground_truth": (
            "Nach deutschem Energierecht (§36 EnWG) werden Kunden, die in eine an das Netz "
            "angeschlossene Wohnung einziehen, automatisch in die Grundversorgung des "
            "zuständigen Versorgers aufgenommen, wenn kein anderer Liefervertrag besteht. "
            "Dies ist eine gesetzliche Pflicht und erfordert keinen aktiven Vertragsabschluss. "
            "Die Grundversorgung ist durch die StromGVV geregelt."
        ),
        "document": "strom",
    },
    {
        "question": "Wieso zahle ich für meinen Strom, obwohl die Wohnung leer steht?",
        "ground_truth": (
            "Wenn ein Kunde auszieht, ohne DEW21 gemäß §19.1 AGB Strom rechtzeitig zu "
            "informieren, haftet er für weitere Entnahmen an der bisherigen Lieferstelle. "
            "Außerdem werden monatliche Abschlagszahlungen auf Basis des geschätzten "
            "Jahresverbrauchs erhoben (§6.1) und laufen weiter, bis DEW21 über den Auszug "
            "informiert wird oder der Vertrag formal beendet ist."
        ),
        "document": "strom",
    },
]
