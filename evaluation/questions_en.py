# DEW21 English evaluation questions
# Format: { question, ground_truth, document_filter }

QUESTIONS_EN = [
    # ── AGB Strom ──────────────────────────────────────────────────────────
    {
        "question": "What is the notice period for cancelling an electricity contract?",
        "ground_truth": "The customer can cancel the electricity contract with four weeks' notice to the end of a calendar month. DEW21 can cancel with six weeks' notice to the end of a calendar month.",
        "document": "strom",
    },
    {
        "question": "What happens if a customer does not pay their electricity bill?",
        "ground_truth": "In the event of payment default, DEW21 may interrupt the electricity supply after a prior reminder. Additionally, default interest and reminder fees may be charged. DEW21 is entitled to request a security deposit.",
        "document": "strom",
    },
    {
        "question": "Can DEW21 adjust electricity prices and how is the customer informed?",
        "ground_truth": "DEW21 can adjust prices and must inform the customer in text form at least six weeks before the planned effective date of the change. The customer then has a special right of termination.",
        "document": "strom",
    },
    {
        "question": "Who is liable for damages caused by electricity outages?",
        "ground_truth": "DEW21 is only liable for interruptions to the electricity supply in cases of intent and gross negligence. In cases of simple negligence, liability is limited to foreseeable damages. Force majeure excludes liability.",
        "document": "strom",
    },
    {
        "question": "What is an advance payment instalment and when is it due?",
        "ground_truth": "An advance payment instalment is a monthly prepayment towards the estimated annual consumption. The amount is based on the previous year's consumption or an estimate. The exact due date is stated on the invoice.",
        "document": "strom",
    },

    # ── AGB Erdgas ──────────────────────────────────────────────────────────
    {
        "question": "How can I cancel my natural gas contract?",
        "ground_truth": "The gas contract can be cancelled in writing or text form with four weeks' notice to the end of a calendar month. Extraordinary termination is possible in the event of a price adjustment.",
        "document": "erdgas",
    },
    {
        "question": "How is gas consumption measured and billed?",
        "ground_truth": "Gas consumption is measured via a meter. Billing is usually done once a year based on actual consumption. Monthly advance payments are collected in the interim.",
        "document": "erdgas",
    },
    {
        "question": "What are the customer's obligations regarding the gas meter?",
        "ground_truth": "The customer is obliged to keep the meter accessible and grant DEW21 access for reading. Any damage to the meter must be reported immediately. The customer must not interfere with the meter.",
        "document": "erdgas",
    },

    # ── SCHUFA ──────────────────────────────────────────────────────────────
    {
        "question": "Why does DEW21 use SCHUFA credit checks?",
        "ground_truth": "DEW21 uses SCHUFA credit information to assess the customer's creditworthiness before entering into a contract. The information is used to evaluate whether the customer is likely to meet their payment obligations.",
        "document": "schufa",
    },
    {
        "question": "What personal data is transmitted to SCHUFA?",
        "ground_truth": "Personal data such as name, address and date of birth, as well as information about the establishment, execution and termination of the contractual relationship, is transmitted to SCHUFA. Negative payment experiences may also be reported.",
        "document": "schufa",
    },
    {
        "question": "Can I object to my data being shared with SCHUFA?",
        "ground_truth": "The transmission of data to SCHUFA is based on a legitimate interest. There is no general right of objection, however data subjects may object in specific cases where special circumstances exist.",
        "document": "schufa",
    },

]
