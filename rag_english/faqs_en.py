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
        "question": "Why is DEW21 checking my credit with SCHUFA?",
        "answer": "DEW21 uses SCHUFA credit information to assess whether a customer is likely to meet their payment obligations before entering into a contract. The legal basis is legitimate interest (Art. 6(1)(f) GDPR). SCHUFA score values support DEW21's risk management but are not the sole basis for decisions.",
        "document": "schufa",
    },
    {
        "question": "Can I stop DEW21 from sharing my data with SCHUFA?",
        "answer": "The transmission is based on legitimate interest and there is no general right of objection. However, under Art. 21(1) GDPR you may object if you can demonstrate specific reasons arising from your particular situation. The objection must be addressed to SCHUFA Holding AG in writing.",
        "document": "schufa",
    },
]
