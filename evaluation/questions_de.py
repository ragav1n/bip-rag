# DEW21 German evaluation questions
# Format: { question, ground_truth, document_filter }
# ground_truth = the correct answer (used to score Context Recall + Answer Correctness)

QUESTIONS_DE = [
    # ── AGB Strom ──────────────────────────────────────────────────────────
    {
        "question": "Wie lange ist die Kündigungsfrist für den Stromvertrag?",
        "ground_truth": "Der Kunde kann den Stromvertrag mit einer Frist von vier Wochen zum Ende eines Kalendermonats kündigen. DEW21 kann den Vertrag mit einer Frist von sechs Wochen zum Ende eines Kalendermonats kündigen.",
        "document": "strom",
    },
    {
        "question": "Was passiert, wenn ein Kunde die Stromrechnung nicht bezahlt?",
        "ground_truth": "Bei Zahlungsverzug kann DEW21 nach vorheriger Mahnung die Stromlieferung unterbrechen. Zusätzlich können Verzugszinsen und Mahnkosten erhoben werden. DEW21 ist berechtigt, eine Sicherheitsleistung zu verlangen.",
        "document": "strom",
    },
    {
        "question": "Kann DEW21 die Strompreise anpassen, und wie wird der Kunde informiert?",
        "ground_truth": "DEW21 kann die Preise anpassen und muss den Kunden mindestens sechs Wochen vor dem geplanten Inkrafttreten der Änderung in Textform informieren. Der Kunde hat dann ein Sonderkündigungsrecht.",
        "document": "strom",
    },
    {
        "question": "Wer haftet bei Schäden durch Stromunterbrechungen?",
        "ground_truth": "DEW21 haftet bei Unterbrechungen der Stromversorgung nur für Vorsatz und grobe Fahrlässigkeit. Bei einfacher Fahrlässigkeit ist die Haftung auf vorhersehbare Schäden begrenzt. Höhere Gewalt schließt die Haftung aus.",
        "document": "strom",
    },
    {
        "question": "Was ist ein Abschlag und wann wird er fällig?",
        "ground_truth": "Ein Abschlag ist eine monatliche Vorauszahlung auf den geschätzten Jahresverbrauch. Die Höhe richtet sich nach dem Vorjahresverbrauch oder einer Schätzung. Der genaue Fälligkeitstermin ist in der Rechnung angegeben.",
        "document": "strom",
    },

    # ── AGB Erdgas ──────────────────────────────────────────────────────────
    {
        "question": "Wie kann ich meinen Erdgasvertrag kündigen?",
        "ground_truth": "Der Erdgasvertrag kann schriftlich oder in Textform mit einer Kündigungsfrist von vier Wochen zum Ende eines Kalendermonats gekündigt werden. Eine außerordentliche Kündigung ist bei einer Preisanpassung möglich.",
        "document": "erdgas",
    },
    {
        "question": "Wie wird der Gasverbrauch gemessen und abgerechnet?",
        "ground_truth": "Der Gasverbrauch wird über einen Zähler gemessen. Die Abrechnung erfolgt in der Regel einmal jährlich auf Basis des tatsächlichen Verbrauchs. Zwischenzeitlich werden monatliche Abschläge erhoben.",
        "document": "erdgas",
    },
    {
        "question": "Was passiert bei einem Gasausfall oder einer Versorgungsunterbrechung?",
        "ground_truth": "Bei Versorgungsunterbrechungen informiert DEW21 die Kunden so früh wie möglich. Geplante Unterbrechungen werden rechtzeitig angekündigt. Bei ungeplanten Ausfällen bemüht sich DEW21 um schnelle Behebung. Eine Haftung bei höherer Gewalt ist ausgeschlossen.",
        "document": "erdgas",
    },
    {
        "question": "Welche Pflichten hat der Kunde bezüglich des Gaszählers?",
        "ground_truth": "Der Kunde ist verpflichtet, den Zähler zugänglich zu halten und DEW21 Zutritt zur Ablesung zu gewähren. Beschädigungen am Zähler sind unverzüglich zu melden. Der Kunde darf keine Eingriffe am Zähler vornehmen.",
        "document": "erdgas",
    },

    # ── SCHUFA ──────────────────────────────────────────────────────────────
    {
        "question": "Wozu nutzt DEW21 die SCHUFA-Auskunft?",
        "ground_truth": "DEW21 nutzt die SCHUFA-Auskunft zur Prüfung der Bonität des Kunden vor Vertragsabschluss. Anhand der Informationen wird bewertet, ob der Kunde voraussichtlich seinen Zahlungsverpflichtungen nachkommen kann.",
        "document": "schufa",
    },
    {
        "question": "Welche Daten werden an die SCHUFA weitergegeben?",
        "ground_truth": "An die SCHUFA werden personenbezogene Daten wie Name, Anschrift, Geburtsdatum sowie Informationen über die Begründung, Durchführung und Beendigung des Vertragsverhältnisses übermittelt. Negative Zahlungserfahrungen können ebenfalls gemeldet werden.",
        "document": "schufa",
    },
    {
        "question": "Kann ich der Weitergabe meiner Daten an die SCHUFA widersprechen?",
        "ground_truth": "Die Datenübermittlung an die SCHUFA erfolgt auf Basis eines berechtigten Interesses. Ein allgemeines Widerspruchsrecht besteht nicht, jedoch können Betroffene in bestimmten Fällen Widerspruch einlegen, wenn besondere Umstände vorliegen.",
        "document": "schufa",
    },

    # ── Creditreform ────────────────────────────────────────────────────────
    {
        "question": "Was ist Creditreform und warum nutzt DEW21 diese?",
        "ground_truth": "Creditreform ist eine Wirtschaftsauskunftei, die Bonitätsinformationen über Unternehmen und Privatpersonen bereitstellt. DEW21 nutzt Creditreform zur Bonitätsprüfung, um das Zahlungsausfallrisiko bei Vertragsabschluss zu minimieren.",
        "document": "creditreform",
    },
    {
        "question": "Wann schaltet DEW21 Creditreform ein?",
        "ground_truth": "DEW21 kann Creditreform zur Bonitätsprüfung vor oder bei Vertragsabschluss einschalten, wenn Anhaltspunkte für ein erhöhtes Zahlungsausfallrisiko bestehen. Dies dient der Absicherung des Unternehmens.",
        "document": "creditreform",
    },
]
