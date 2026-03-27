# DEW21-provided English evaluation questions
# Ground truths derived from: AGB Strom §22, Anhang SCHUFA, Anhang Creditreform

QUESTIONS_DEW21_EN = [

    # ── 1. General legal advice ──────────────────────────────────────────────

    {
        "question": "Am I allowed to share this customer data?",
        "ground_truth": (
            "DEW21 may share customer data with SCHUFA and Creditreform based on "
            "Article 6(1)(b) and (f) GDPR for creditworthiness checks and to protect "
            "against payment default. Data is only shared if a legitimate interest "
            "exists and does not outweigh the customer's rights. Personal data is not "
            "transmitted to third countries (§22.4e, §22.6 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "What data am I allowed to store for this process?",
        "ground_truth": (
            "DEW21 may store: customer contact details (name, address, email, phone), "
            "delivery address data (meter number, market location ID), consumption data, "
            "supply period information, billing data (bank details), and payment behaviour "
            "data. Processing must have a legal basis under Art. 6 GDPR (§22.3 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "Do I need to obtain consent?",
        "ground_truth": (
            "Consent (Art. 6(1)(a) GDPR) is required specifically for telephone marketing. "
            "For contract fulfilment, legal obligations, and legitimate interests, consent "
            "is not required — Art. 6(1)(b), (c), and (f) GDPR apply instead. "
            "SCHUFA and Creditreform data transmissions are based on legitimate interest "
            "(Art. 6(1)(f) GDPR), not consent (§22.4 AGB Strom)."
        ),
        "document": None,
    },
    {
        "question": "What legal requirements apply to district heating contracts?",
        "ground_truth": (
            "The available DEW21 documents cover electricity and natural gas supply contracts "
            "only. District heating (Fernwärme) contracts are not addressed in the current "
            "document base and would require separate regulatory documentation."
        ),
        "document": None,
    },
    {
        "question": "What information obligations do energy companies have towards their customers?",
        "ground_truth": (
            "DEW21 must inform customers of: price changes at least 6 weeks before they take "
            "effect (§9.13); contract amendments at least 6 weeks in advance (§21.2); "
            "the special termination right when prices or contract terms change; "
            "the responsible network operator (§12); and dispute resolution options "
            "including the Schlichtungsstelle Energie (§23.1 AGB Strom)."
        ),
        "document": "strom",
    },
    {
        "question": "What legal regulations apply in the event of account suspensions or debt collection procedures?",
        "ground_truth": (
            "DEW21 may suspend supply if the outstanding amount equals twice the monthly "
            "instalment or at least €100, including collection costs. The customer must be "
            "notified at least 4 weeks before interruption. Debt collection costs (lawyers, "
            "debt collection agencies) may be charged to the customer under §288 BGB. "
            "The minimum amount thresholds of §19(2) StromGVV must be met (§7.5 AGB Strom)."
        ),
        "document": "strom",
    },
    {
        "question": "What information must be included in written correspondence from a legal standpoint?",
        "ground_truth": (
            "Written notifications from DEW21 must include: the intended effective date and "
            "reasons for price or contract changes; the customer's special right of termination "
            "and the deadline to exercise it; for suspension notices, the planned date of "
            "interruption at least 4 weeks in advance. Contract termination confirmations must "
            "specify the end date (§9.13, §18.1, §21.2 AGB Strom)."
        ),
        "document": "strom",
    },

    # ── 2. Data protection & GDPR ────────────────────────────────────────────

    {
        "question": "How long are we allowed to store this data?",
        "ground_truth": (
            "Under §22.7 AGB Strom, personal data is stored only as long as necessary for "
            "its purpose. Marketing data is deleted no later than 12 months after contract end. "
            "SCHUFA stores data for a standard period of 3 years after completion. "
            "Creditreform stores data for an initial period of 4 years, then reviews necessity; "
            "data is deleted exactly 3 years after completion of a matter."
        ),
        "document": None,
    },
    {
        "question": "What legal risks are associated with this response to the customer?",
        "ground_truth": (
            "The available DEW21 documents do not provide general legal risk assessment "
            "for individual customer responses. Legal risk evaluation would require "
            "case-specific legal advice beyond the scope of these terms and conditions documents."
        ),
        "document": None,
    },

    # ── 3. Legal decision support ────────────────────────────────────────────

    {
        "question": "What possible scenarios are there in this case?",
        "ground_truth": (
            "The available documents do not support open-ended case scenario analysis. "
            "The AGB Strom covers specific scenarios such as payment default (§7.5), "
            "supply interruption (§7.5), price disputes (§10), and extraordinary termination (§18.2), "
            "but a general scenario overview depends on the specific case context."
        ),
        "document": "strom",
    },
    {
        "question": "What is the risk level associated with these options?",
        "ground_truth": (
            "Risk level assessment is not covered by the available DEW21 documents. "
            "The documents provide contractual obligations and legal bases but do not "
            "quantify or categorise risk levels for specific decisions."
        ),
        "document": None,
    },
    {
        "question": "What would be the formally correct next step?",
        "ground_truth": (
            "The formally correct next step depends on the situation. For payment default: "
            "send a reminder, then notify the customer 4 weeks before suspension (§7.5). "
            "For price changes: notify the customer in writing at least 6 weeks in advance "
            "with information on the special termination right (§9.13). "
            "For contract disputes: refer to the Schlichtungsstelle Energie (§23.1)."
        ),
        "document": "strom",
    },

    # ── 4. Typical customer questions ────────────────────────────────────────

    {
        "question": "Why am I being registered for basic coverage, even though I haven't signed a contract?",
        "ground_truth": (
            "Under German energy law (§36 EnWG), customers who move into a property connected "
            "to the grid are automatically included in the basic supply (Grundversorgung) of the "
            "local provider if no other supply contract exists. This is a statutory obligation "
            "and does not require the customer to actively sign a contract. DEW21's standard "
            "AGBs apply to customers who have signed a supply agreement; the Grundversorgung "
            "regime is governed by the StromGVV regulation."
        ),
        "document": "strom",
    },
    {
        "question": "Why am I paying for electricity when the apartment is empty?",
        "ground_truth": (
            "If a customer moves out without notifying DEW21 in advance as required by §19.1 "
            "AGB Strom, they remain liable for any continued withdrawals at the previous "
            "delivery location. Additionally, monthly advance payments are based on estimated "
            "annual consumption (§6.1) and continue until DEW21 is informed of the move or "
            "the contract is formally terminated."
        ),
        "document": "strom",
    },
]
