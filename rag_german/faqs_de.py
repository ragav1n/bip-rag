"""
DEW21 FAQ-Paare — Deutsch
Jeder Eintrag wird als "F: ... A: ..." eingebettet, damit natürlichsprachliche
Kundenfragen direkt auf FAQ-Einträge matchen und die Vokabular-Lücke zu den
juristischen Dokumenten überbrückt wird.
"""

FAQS_DE = [
    # ── Abrechnung / Grundpreis ───────────────────────────────────────────────
    {
        "question": "Warum zahle ich Strom, obwohl die Wohnung leer steht?",
        "answer": "Der Basispreis (§9.1) enthält einen verbrauchsunabhängigen Basisgrundpreis, der unabhängig vom tatsächlichen Verbrauch erhoben wird — also auch bei Nullverbrauch. Er deckt Fixkosten wie Messstellenbetrieb und Netzanschluss ab. Diese Kosten entfallen erst mit Kündigung des Vertrags.",
        "document": "strom",
    },
    {
        "question": "Muss ich zahlen, wenn ich keinen Strom verbrauche?",
        "answer": "Ja. Der Basispreis (§9.1) besteht aus einem verbrauchsunabhängigen Basisgrundpreis, der auch bei Nullverbrauch anfällt. Nur der verbrauchsabhängige Arbeitspreis entfällt bei keinem Verbrauch.",
        "document": "strom",
    },
    {
        "question": "Was ist der Grundpreis und was deckt er ab?",
        "answer": "Der Basispreis (§9.1) setzt sich aus einem verbrauchsunabhängigen Basisgrundpreis und einem verbrauchsabhängigen Arbeitspreis zusammen. Er deckt die Kosten der Versorgung aller Kunden im Tarif ab, einschließlich Messstellenbetrieb, Netzentgelt, Konzessionsabgabe sowie Steuern und Abgaben.",
        "document": "strom",
    },
    {
        "question": "Warum bekomme ich eine Gasrechnung, obwohl ich kein Gas verbraucht habe?",
        "answer": "Der Gaspreis enthält einen verbrauchsunabhängigen Basisgrundpreis (§9.1), der unabhängig vom Verbrauch anfällt. Fixkosten wie Messstellenbetrieb und Netzentgelt entstehen auch ohne Verbrauch. Der Vertrag muss gekündigt werden, um diese Kosten zu beenden.",
        "document": "erdgas",
    },
    {
        "question": "Welche Fixkosten fallen auch ohne Verbrauch an?",
        "answer": "Der verbrauchsunabhängige Basisgrundpreis (§9.1), die Messstellenbetriebsgebühr (§9.4) und der Netzgrundpreis (§9.3) werden unabhängig vom tatsächlichen Verbrauch erhoben. Sie decken die Fixkosten der Anschlussbereitstellung.",
        "document": "strom",
    },

    # ── Kündigung ─────────────────────────────────────────────────────────────
    {
        "question": "Wie lange ist die Kündigungsfrist beim Stromvertrag?",
        "answer": "Die ordentliche Kündigungsfrist beträgt für beide Seiten einen Monat in Textform (§18.1). DEW21 bestätigt die Kündigung innerhalb einer Woche schriftlich. Eine außerordentliche Kündigung ohne Frist ist aus wichtigem Grund nach §18.2 möglich.",
        "document": "strom",
    },
    {
        "question": "Kann ich sofort kündigen, wenn die Preise steigen?",
        "answer": "Ja. Bei einer Preisanpassung durch DEW21 haben Sie das Recht, den Vertrag ohne Einhaltung einer Kündigungsfrist zum Zeitpunkt des Wirksamwerdens der Preisanpassung zu kündigen (§9.13). DEW21 muss Sie in der Preisänderungsmitteilung ausdrücklich auf dieses Recht hinweisen.",
        "document": "strom",
    },
    {
        "question": "Wie kündige ich meinen Gasvertrag beim Auszug?",
        "answer": "Teilen Sie DEW21 den Umzug mindestens 10 Werktage vor dem Umzugsdatum schriftlich mit, inklusive Umzugsdatum, neuer Adresse und Gaszählernummer (§19.1). Der Vertrag endet zum Auszugstermin, wenn die Mitteilung rechtzeitig erfolgt.",
        "document": "erdgas",
    },

    # ── Zahlungsverzug ────────────────────────────────────────────────────────
    {
        "question": "Was passiert, wenn ich eine Rechnung nicht bezahle?",
        "answer": "Erreicht der Rückstand das Doppelte der monatlichen Abschlagszahlung oder mindestens 100 € inkl. Mahn- und Inkassokosten (§7.5), darf DEW21 die Lieferung einstellen und den Netzbetreiber beauftragen, die Verbindung zu unterbrechen. Der Netzbetreiber benötigt dafür weitere sechs Werktage. Eine Unterbrechung unterbleibt, wenn die Folgen außer Verhältnis zur Schuld stehen.",
        "document": "strom",
    },
    {
        "question": "Darf DEW21 mir den Strom abstellen, wenn ich nicht zahle?",
        "answer": "Ja, unter den Voraussetzungen von §7.5: wenn der Rückstand das Doppelte des monatlichen Abschlags oder mindestens 100 € erreicht. Der Netzbetreiber führt die Unterbrechung nach weiteren sechs Werktagen durch. Bei unverhältnismäßigen Folgen oder Aussicht auf Zahlung wird nicht unterbrochen.",
        "document": "strom",
    },

    # ── Preisänderungen ───────────────────────────────────────────────────────
    {
        "question": "Wie viel Vorlauf muss DEW21 bei einer Preiserhöhung geben?",
        "answer": "DEW21 muss mindestens sechs Wochen vor dem geplanten Wirksamwerden der Preisänderung in Textform informieren (§9.13). Gleichzeitig werden die Änderungen auf der DEW21-Website veröffentlicht. Der Kunde hat dann das Recht zur fristlosen Kündigung.",
        "document": "strom",
    },

    # ── Umzug ─────────────────────────────────────────────────────────────────
    {
        "question": "Was muss ich beim Auszug tun?",
        "answer": "Teilen Sie DEW21 den Umzug mindestens 10 Werktage vorher schriftlich mit (§19.1): Umzugsdatum, neue Anschrift und Zählernummer bzw. Marktlokations-ID. DEW21 meldet Sie daraufhin beim Netzbetreiber ab.",
        "document": "strom",
    },

    # ── SCHUFA ────────────────────────────────────────────────────────────────
    {
        "question": "Werden meine Identitätsdaten unter einer anderen Kategorie verarbeitet als meine Finanzdaten?",
        "answer": "Sowohl Identitätsdaten (Name, Adresse, Geburtsdatum) als auch Finanzdaten (Zahlungsverhalten, Kredithistorie, Zahlungsausfälle) werden auf derselben Rechtsgrundlage verarbeitet: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse). Sie fallen nicht in separate rechtliche Kategorien. Besondere Kategorien nach Art. 9 DSGVO — wie ethnische Herkunft, politische Überzeugungen oder Gesundheitsdaten — werden von der SCHUFA ausdrücklich nicht gespeichert oder verarbeitet.",
        "document": "schufa",
    },
    {
        "question": "Warum prüft DEW21 meine Bonität bei der SCHUFA?",
        "answer": "DEW21 nutzt SCHUFA-Informationen, um vor Vertragsabschluss zu prüfen, ob ein Kunde seinen Zahlungsverpflichtungen voraussichtlich nachkommen kann. Rechtsgrundlage ist das berechtigte Interesse (Art. 6 Abs. 1 lit. f DSGVO). SCHUFA-Scorewerte fließen in das Risikomanagement ein, sind aber nicht alleinige Entscheidungsgrundlage.",
        "document": "schufa",
    },
    {
        "question": "Kann ich der Datenweitergabe an die SCHUFA widersprechen?",
        "answer": "Ein allgemeines Widerspruchsrecht besteht nicht, da die Übermittlung auf berechtigtem Interesse basiert. Nach Art. 21 Abs. 1 DSGVO können Sie jedoch Widerspruch einlegen, wenn Sie besondere Gründe aus Ihrer persönlichen Situation nachweisen können. Der Widerspruch ist schriftlich an die SCHUFA Holding AG zu richten.",
        "document": "schufa",
    },

    # ── Creditreform ──────────────────────────────────────────────────────────
    {
        "question": "Wie lange speichert Creditreform meine Daten?",
        "answer": "Creditreform speichert Daten solange, wie ihre Kenntnis für die Erfüllung des Zwecks notwendig ist. In der Regel beträgt die Speicherdauer zunächst vier Jahre. Nach Ablauf wird geprüft, ob eine weitere Speicherung notwendig ist; andernfalls werden die Daten taggenau gelöscht. Im Falle der Erledigung eines Sachverhalts werden die Daten drei Jahre nach Erledigung taggenau gelöscht. Eintragungen im Schuldnerverzeichnis werden gemäß § 882e ZPO nach drei Jahren seit der Eintragungsanordnung taggenau gelöscht.",
        "document": "creditreform",
    },
    {
        "question": "Was ist die Speicherfrist bei Creditreform?",
        "answer": "Die reguläre Speicherdauer bei Creditreform beträgt zunächst vier Jahre. Nach Ablauf dieser Frist wird geprüft, ob eine weitere Speicherung erforderlich ist. Erledigte Sachverhalte werden drei Jahre nach Erledigung gelöscht. Einträge im Schuldnerverzeichnis werden nach drei Jahren gemäß § 882e ZPO gelöscht.",
        "document": "creditreform",
    },
    {
        "question": "Wie unterscheiden sich die Speicherfristen von SCHUFA und Creditreform?",
        "answer": "SCHUFA: allgemeine Daten drei Jahre nach Erledigung; störungsfreie Vertragsdaten werden bei Beendigungsmeldung sofort gelöscht; Schuldnerregisterdaten drei Jahre (oder früher auf Gerichtsbeschluss); Insolvenz-/Restschulddaten genau drei Jahre nach Verfahrensende; Vorankündigungen drei Jahre plus weitere drei Jahre Prüfungsfrist. Creditreform: reguläre Speicherdauer zunächst vier Jahre; nach vier Jahren Prüfung ob weitere Speicherung nötig; erledigte Sachverhalte drei Jahre nach Erledigung gelöscht; Schuldnerregistereinträge nach drei Jahren gemäß § 882e ZPO.",
        "document": "creditreform",
    },
    {
        "question": "Warum gibt DEW21 meine Daten an Creditreform weiter?",
        "answer": "DEW21 übermittelt Kundendaten an die Creditreform Dortmund/Witten Scharf KG zur Bonitätsprüfung vor Vertragsabschluss. Rechtsgrundlage ist das berechtigte Interesse gemäß Art. 6 Abs. 1 lit. f DSGVO. Creditreform speichert Angaben zu Name, Anschrift, Familienstand, Beruf, wirtschaftlichen Verhältnissen, Verbindlichkeiten und Zahlungsverhalten.",
        "document": "creditreform",
    },
    {
        "question": "Welche Daten speichert Creditreform über mich?",
        "answer": "Creditreform speichert insbesondere Name, Firmierung, Anschrift, Familienstand, Berufstätigkeit, wirtschaftliche Verhältnisse, bestehende Verbindlichkeiten sowie Informationen zum Zahlungsverhalten. Diese Daten stammen teils aus öffentlich zugänglichen Quellen (Register, Internet, Presse) und teils aus übermittelten Daten zu offenen Forderungen.",
        "document": "creditreform",
    },
    {
        "question": "Kann ich der Verarbeitung meiner Daten durch Creditreform widersprechen?",
        "answer": "Ein Widerspruch gegen die Datenverarbeitung durch Creditreform ist nur möglich, wenn besondere Gründe aus der eigenen Situation nachgewiesen werden können. Werden solche Gründe nachgewiesen, werden die Daten nicht mehr verarbeitet. Die Verarbeitung erfolgt aus zwingenden schutzwürdigen Gründen des Gläubiger- und Kreditschutzes, die regelmäßig überwiegen.",
        "document": "creditreform",
    },
    {
        "question": "Welche Rechte habe ich gegenüber Creditreform?",
        "answer": "Sie haben das Recht auf Auskunft über die gespeicherten Daten. Bei falschen Daten haben Sie Anspruch auf Berichtigung oder Löschung. Kann die Richtigkeit nicht sofort festgestellt werden, haben Sie ein Recht auf Sperrung. Bei unvollständigen Daten haben Sie das Recht auf Ergänzung. Eine erteilte Einwilligung zur Datenverarbeitung kann jederzeit widerrufen werden.",
        "document": "creditreform",
    },
]
