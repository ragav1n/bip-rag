"""
DEW21 FAQ pairs — English
Each entry is embedded as "Q: ... A: ..." so natural language questions
match FAQ entries directly, bridging the vocabulary gap to legal documents.
"""

FAQS_EN = [
    # ── Billing / Charges ────────────────────────────────────────────────────
    {
        "question": "Why am I paying for electricity when the apartment is empty?",
        "answer": "The price structure includes a consumption-independent base rate (Basisgrundpreis, §9.1) that is charged regardless of how much electricity you use — even zero. It covers fixed infrastructure costs such as meter operation and grid connection. You only avoid this charge by terminating the contract.",
        "document": "strom",
    },
    {
        "question": "Do I have to pay even if I don't use any electricity?",
        "answer": "Yes. The base price (§9.1) has a consumption-independent annual base rate that applies even with zero consumption. Only the usage-dependent component is zero when there is no consumption.",
        "document": "strom",
    },
    {
        "question": "What is the base price and what does it cover?",
        "answer": "The base price (§9.1) consists of an annual consumption-independent base rate and a consumption-dependent usage rate. It covers the costs of supplying all customers under the tariff, including meter operation fees, grid fees, concession fees, taxes, and levies.",
        "document": "strom",
    },
    {
        "question": "Why am I paying a gas bill if I haven't used any gas?",
        "answer": "The gas price structure includes a consumption-independent base rate (§9.1) charged regardless of consumption. Fixed infrastructure costs such as meter operation and grid fees apply even with zero usage. The contract must be terminated to stop these charges.",
        "document": "erdgas",
    },
    {
        "question": "What fixed costs apply even without consumption?",
        "answer": "The consumption-independent base rate (§9.1), meter operation fees (§9.4), and grid base fees (§9.3) are charged regardless of actual consumption. These cover the fixed costs of maintaining your connection.",
        "document": "strom",
    },

    # ── Cancellation ─────────────────────────────────────────────────────────
    {
        "question": "How much notice do I need to cancel my electricity contract?",
        "answer": "The standard notice period is one month in writing for both parties (§18.1). DEW21 confirms the termination in writing within one week. Extraordinary termination without notice is possible for important reasons under §18.2.",
        "document": "strom",
    },
    {
        "question": "Can I cancel immediately if prices go up?",
        "answer": "Yes. If DEW21 adjusts prices, you have the right to terminate the contract without any notice period at the moment the price adjustment takes effect (§9.13). DEW21 must inform you of this right in the price change notification.",
        "document": "strom",
    },
    {
        "question": "How do I cancel my gas contract when moving out?",
        "answer": "Notify DEW21 of your move in writing at least 10 business days before the move date, including the move date, new address, and meter number (§19.1). The contract ends at the move-out date if you notify in time.",
        "document": "erdgas",
    },

    # ── Payments / Default ────────────────────────────────────────────────────
    {
        "question": "What happens if I miss a payment?",
        "answer": "If the overdue amount reaches double the monthly advance payment or at least €100 including reminder fees (§7.5), DEW21 may suspend supply and instruct the network operator to interrupt the connection. The interruption requires six additional working days. DEW21 may also request an advance payment (§8.1).",
        "document": "strom",
    },
    {
        "question": "Can DEW21 cut off my electricity for non-payment?",
        "answer": "Yes. Under §7.5, DEW21 may suspend supply if the overdue amount reaches double the monthly advance payment or at least €100. The network operator requires six further working days to carry out the interruption. Interruption is not carried out if consequences are disproportionate to the default.",
        "document": "strom",
    },

    # ── Price changes ─────────────────────────────────────────────────────────
    {
        "question": "How much notice must DEW21 give before raising prices?",
        "answer": "DEW21 must notify you in writing at least six weeks before the intended price change takes effect (§9.13). At the same time, the changes are published on the DEW21 website. You then have the right to cancel without notice.",
        "document": "strom",
    },

    # ── Moving ────────────────────────────────────────────────────────────────
    {
        "question": "What do I need to do when I move out?",
        "answer": "Notify DEW21 in writing at least 10 business days before the move date (§19.1), providing the move date, new address, and electricity meter number or market location ID. DEW21 then deregisters you with the network operator.",
        "document": "strom",
    },

    # ── SCHUFA ────────────────────────────────────────────────────────────────
    {
        "question": "Is my identity information processed under a different category than my financial data?",
        "answer": "Both identity data (name, address, date of birth) and financial data (payment behavior, credit history, defaults) are processed under the same legal basis: Art. 6(1)(f) GDPR (legitimate interest). They are not in separate legal categories. However, special categories under Art. 9 GDPR — such as ethnic origin, political beliefs, and health data — are explicitly not stored or processed by SCHUFA.",
        "document": "schufa",
    },
    {
        "question": "Why is DEW21 checking my credit with SCHUFA?",
        "answer": "DEW21 uses SCHUFA credit information to assess whether a customer is likely to meet their payment obligations before entering into a contract. The legal basis is legitimate interest (Art. 6(1)(f) GDPR). SCHUFA score values support DEW21's risk management but are not the sole basis for decisions.",
        "document": "schufa",
    },
    {
        "question": "Can I stop DEW21 from sharing my data with SCHUFA?",
        "answer": "The transmission is based on legitimate interest and there is no general right of objection. However, under Art. 21(1) GDPR you may object if you can demonstrate specific reasons arising from your particular situation. The objection must be addressed to SCHUFA Holding AG in writing.",
        "document": "schufa",
    },

    # ── Creditreform ──────────────────────────────────────────────────────────
    {
        "question": "How long does Creditreform store my data?",
        "answer": "Creditreform stores data for as long as necessary to fulfill the purpose of storage. As a rule, the initial storage period is four years. After this period, it is checked whether further storage is still necessary; if not, the data is deleted on the exact date. If a matter is resolved, the data is deleted three years after resolution. Entries in the debtor registry are deleted three years after the date of the entry order in accordance with § 882e ZPO.",
        "document": "creditreform",
    },
    {
        "question": "What is the data retention period for Creditreform?",
        "answer": "Creditreform retains data for an initial period of four years as a general rule. After four years, it is reviewed whether continued storage is necessary; otherwise data is deleted on the exact date. Resolved matters are deleted three years after resolution. Debtor registry entries are deleted after three years per § 882e ZPO.",
        "document": "creditreform",
    },
    {
        "question": "How do SCHUFA and Creditreform data retention periods compare?",
        "answer": "SCHUFA: general data is stored three years from completion; trouble-free contract data is deleted immediately upon termination notification; debtor register data three years (or earlier by court order); insolvency/debt relief data exactly three years after the end of proceedings; advance notices three years plus a further three-year assessment period. Creditreform: data is stored for an initial four-year period as a general rule; after four years it is reviewed whether further storage is needed; resolved matters are deleted three years after resolution; debtor registry entries deleted after three years per § 882e ZPO.",
        "document": "creditreform",
    },
    {
        "question": "Why does DEW21 share my data with Creditreform?",
        "answer": "DEW21 transmits customer data to Creditreform Dortmund/Witten Scharf KG to assess creditworthiness before entering into a contract. The legal basis is legitimate interest under Art. 6(1)(f) GDPR. Creditreform stores information on name, address, marital status, professional activity, financial circumstances, liabilities, and payment behavior.",
        "document": "creditreform",
    },
    {
        "question": "What data does Creditreform store about me?",
        "answer": "Creditreform stores information including name, company name, address, marital status, professional activity, financial circumstances, existing liabilities, and payment behavior. This data comes partly from publicly accessible sources (registers, internet, press) and partly from transmitted data on outstanding claims.",
        "document": "creditreform",
    },
    {
        "question": "Can I object to Creditreform processing my data?",
        "answer": "You can only object to Creditreform processing your data if you can demonstrate specific reasons arising from your particular situation. If such reasons are proven, the data will no longer be processed. The processing is carried out for compelling legitimate reasons relating to creditor protection and creditworthiness, which regularly outweigh individual interests.",
        "document": "creditreform",
    },
    {
        "question": "What are my rights regarding data stored at Creditreform?",
        "answer": "You have the right to receive information about data stored about you. If data is incorrect, you can request correction or deletion. If correctness cannot be immediately determined, you can request blocking until clarified. If data is incomplete, you have the right to have it completed. You may also withdraw consent at any time, though this does not affect the lawfulness of prior processing.",
        "document": "creditreform",
    },
]
