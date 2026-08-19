# FinCrime typology reference

25 typologies, grouped by family. Every entry cites primary sources; run `python argus.py verify --typologies` to confirm each cited link is still live.

## Contents

**Alternative remittance**
- [Cuckoo smurfing](#cuckoo-smurfing) — `cuckoo-smurfing`
- [Hawala and informal value transfer systems](#hawala-and-informal-value-transfer-systems) — `hawala`

**Banking structures**
- [Correspondent banking and nested accounts](#correspondent-banking-and-nested-accounts) — `correspondent-nested`
- [E-money, fintech and agent network abuse](#e-money-fintech-and-agent-network-abuse) — `emi-fintech`

**Corporate structures**
- [Professional enablers and TCSP abuse](#professional-enablers-and-tcsp-abuse) — `professional-enablers`
- [Shell and shelf companies](#shell-and-shelf-companies) — `shell-companies`

**Corruption**
- [PEP, kleptocracy and grand corruption proceeds](#pep-kleptocracy-and-grand-corruption-proceeds) — `pep-kleptocracy`

**Exploitation**
- [Human trafficking and modern slavery finance](#human-trafficking-and-modern-slavery-finance) — `human-trafficking`

**Fraud & predicate offences**
- [Authorised push payment (APP) fraud](#authorised-push-payment-app-fraud) — `app-fraud`
- [Business email compromise and invoice redirection](#business-email-compromise-and-invoice-redirection) — `bec-invoice`
- [Bust-out fraud](#bust-out-fraud) — `bust-out`
- [Romance and investment fraud (incl. 'pig butchering')](#romance-and-investment-fraud-incl-pig-butchering) — `romance-investment`

**Integration**
- [Gambling and gaming laundering](#gambling-and-gaming-laundering) — `gambling`
- [Real estate laundering](#real-estate-laundering) — `real-estate`

**Layering**
- [Money mule networks](#money-mule-networks) — `money-mules`

**Placement**
- [Cash-intensive business co-mingling](#cash-intensive-business-co-mingling) — `cash-intensive`
- [Structuring / smurfing](#structuring--smurfing) — `structuring`

**Process**
- [SARs, DAML and the reporting mechanics (process explainer)](#sars-daml-and-the-reporting-mechanics-process-explainer) — `sars-daml`

**Sanctions**
- [Proliferation financing](#proliferation-financing) — `proliferation`
- [Sanctions evasion and circumvention](#sanctions-evasion-and-circumvention) — `sanctions-evasion`
- [Shadow fleet and oil price cap evasion](#shadow-fleet-and-oil-price-cap-evasion) — `shadow-fleet`

**Terrorist financing**
- [Charity and NPO abuse for terrorist financing](#charity-and-npo-abuse-for-terrorist-financing) — `npo-abuse`

**Trade & commerce**
- [Trade-based money laundering (TBML)](#trade-based-money-laundering-tbml) — `tbml`

**Virtual assets**
- [Crypto laundering and chain-hopping](#crypto-laundering-and-chain-hopping) — `crypto-laundering`
- [Mixers, tumblers and privacy coins](#mixers-tumblers-and-privacy-coins) — `mixers`

---

# Alternative remittance

## Cuckoo smurfing

*Also called: cuckooing*  ·  id `cuckoo-smurfing`

Criminal cash is deposited into the account of an innocent customer who is expecting a legitimate overseas remittance. The customer receives the amount they expected, so nothing looks wrong to them, while the launderer's overseas funds are retained abroad. It is genuinely hard to detect because the account holder is an unwitting participant.

**How it works**

1. A customer abroad instructs a remittance to a beneficiary in the UK/EU.
2. A complicit broker, instead of transferring funds, arranges for criminal cash to be deposited locally into the beneficiary's account.
3. The beneficiary receives the expected amount and is satisfied.
4. The broker keeps the legitimate overseas funds, which are now clean to them.
5. Deposits are usually structured across branches to avoid attention.

**Impact on banks**

This typology is uniquely damaging because the account holder is innocent and cooperative, so standard 'ask the customer' controls return clean answers. Australian enforcement has shown regulators will penalise firms for missing it, and remediation is painful because it means revisiting customers who did nothing wrong.

**Red flags**

- Third-party cash deposits into a personal account where the holder expected a wire.
- Deposits made in a different city from the account holder's residence.
- Multiple small cash deposits matching the value of an expected remittance.
- Customer cannot identify who made the deposit.
- Pattern repeats across several unconnected customers using the same remitter corridor.

**How to spot it**

- Flag third-party cash deposits into personal accounts where the holder expected an inbound wire.
- Alert on deposit location materially distant from the account holder's residence.
- Look for multiple small cash deposits summing to the value of an expected remittance.
- Investigate at remitter-corridor level, not per customer - the pattern repeats across unrelated holders.
- Ask the customer directly how the funds arrived; unwitting customers usually answer openly.

**What to do as the analyst**

- Ask the customer directly how the funds arrived - unwitting customers usually answer openly.
- Look for deposit-location mismatch as the primary signal.
- Treat the remittance corridor and broker as the investigative unit, not the individual customer.

**Sources**

- [FATF - Publications](https://www.fatf-gafi.org/en/publications.html)
- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)

## Hawala and informal value transfer systems

*Also called: IVTS, underground banking, hundi, fei ch'ien*  ·  id `hawala`

Value moves between brokers who settle among themselves later, so no money crosses a border in the transaction the customer sees. Most hawala is legitimate remittance serving communities that formal banking underserves. The AML concern is that the same settlement mechanics can carry criminal value invisibly, and that unregistered operators fall outside supervision.

**How it works**

1. Customer pays a broker in country A; broker instructs a counterpart in country B to pay out.
2. No cross-border transfer occurs for that transaction - only a message.
3. Brokers net off obligations over time, settling in bulk, via trade, or via cash couriers.
4. Settlement through trade invoices makes this overlap directly with TBML.
5. Criminal value can be injected into an otherwise legitimate remittance flow.

**Impact on banks**

Most informal value transfer is legitimate remittance serving communities that formal banking underserves, and blanket de-risking of the sector is itself a recognised regulatory harm. The bank's real exposure is unregistered operators and inadequate oversight of MSB customers, not the model itself.

**Red flags**

- Business account showing many small third-party credits and periodic large outbound transfers.
- Money service business operating without registration where registration is required.
- Account activity inconsistent with the declared MSB customer base or corridor.
- Bulk settlement payments to trading companies unrelated to the stated business.
- Cash deposits followed by transfers to a small set of overseas counterparties.

**How to spot it**

- Check MSB registration and supervision status first - unregistered operation is the clearest signal.
- Compare corridor volumes against the declared customer base and business size.
- Flag many small third-party credits followed by periodic large outbound transfers.
- Look for bulk settlement payments to trading companies unrelated to the stated business.
- Review the MSB's own AML programme and agent oversight rather than exiting by default.

**What to do as the analyst**

- Check registration/supervision status first - unregistered operation is the clearest signal.
- Do not treat the model itself as inherently suspicious; test the controls around it.
- Look for TBML-style settlement in the same customer group.

**Sources**

- [FATF - Publications](https://www.fatf-gafi.org/en/publications.html)
- [HMRC - Money laundering supervision (GOV.UK)](https://www.gov.uk/guidance/money-laundering-regulations-money-service-business-registration)

---

# Banking structures

## Correspondent banking and nested accounts

*Also called: downstream correspondent clearing, payable-through accounts*  ·  id `correspondent-nested`

A bank provides accounts to another bank, whose own customers - and sometimes their customers' customers - reach the correspondent's payment rails. Nesting means the correspondent is effectively serving parties it never onboarded and cannot see. This is the core reason correspondent relationships attract enhanced due diligence obligations.

**How it works**

1. Respondent bank opens an account with a correspondent to access clearing.
2. Respondent allows its own respondent banks to use that account ('nesting').
3. Payments arrive at the correspondent from parties several layers removed.
4. Payable-through arrangements let respondent customers transact directly.
5. Weak controls at any layer propagate straight to the correspondent.

**Impact on banks**

Correspondent relationships carry mandatory enhanced due diligence precisely because the correspondent serves parties it never onboarded. The largest AML penalties in banking history sit in this category, and the operational risk - loss of dollar clearing - can exceed the fine.

**Red flags**

- Payment volumes far exceeding the respondent's declared size or market.
- Originators and beneficiaries in jurisdictions unrelated to the respondent's stated footprint.
- Incomplete or stripped originator information in payment messages.
- Respondent unwilling to disclose whether it permits nesting.
- Sudden change in transaction mix or corridor without explanation.

**How to spot it**

- Ask explicitly whether the respondent permits nesting and obtain its AML programme.
- Monitor payment volumes against the respondent's declared size and market footprint.
- Alert on originator/beneficiary jurisdictions unrelated to the respondent's stated business.
- Treat incomplete or stripped payment-message fields as a discrete red flag.
- Use the Wolfsberg Correspondent Banking Due Diligence Questionnaire as the baseline.
- Flag sudden changes in transaction mix or corridor without explanation.

**What to do as the analyst**

- Ask explicitly whether nesting is permitted and obtain the respondent's own AML programme.
- Monitor for payment-message field stripping as a discrete red flag.
- Use the Wolfsberg Correspondent Banking Due Diligence Questionnaire as the baseline.

**Sources**

- [Wolfsberg Group - Resources (CBDDQ, correspondent banking)](https://wolfsberg-group.org/resources)
- [EBA - AML/CFT guidelines](https://www.eba.europa.eu/)

## E-money, fintech and agent network abuse

*Also called: EMI abuse, payment agent abuse*  ·  id `emi-fintech`

Fast digital onboarding, distributed agent networks and payment-institution passporting create scale and speed that criminals exploit. Supervisory findings in this sector consistently concern onboarding controls and the oversight of agents and distributors rather than exotic laundering methods.

**How it works**

1. Remote onboarding defeated with synthetic or stolen identity documents.
2. Large numbers of accounts opened rapidly for use as mules.
3. Agents or distributors onboard customers with weaker checks than the principal applies.
4. Passporting used to serve customers in markets the firm barely understands.
5. Funds moved between e-money wallets to layer before hitting the banking system.

**Impact on banks**

Supervisory findings in this sector consistently concern onboarding controls and oversight of agents and distributors rather than exotic laundering methods. Fast growth plus remote onboarding plus passporting is the risk combination regulators look for, and enforcement here has been rising.

**Red flags**

- Bulk account openings sharing device, IP, or document template artefacts.
- Agent locations with anomalous volume relative to local population or trade.
- High proportion of accounts dormant then simultaneously activated.
- Customer base concentrated in a market unrelated to the firm's stated strategy.
- Wallet-to-wallet transfers with no apparent commercial purpose.

**How to spot it**

- Test document authenticity and liveness signals, not merely document presence.
- Detect bulk openings sharing device fingerprints, IP ranges or document template artefacts.
- Review agent-level volume against local population and plausible trade.
- Flag cohorts of dormant accounts activating simultaneously.
- Compare customer-base geography against the firm's stated strategy and risk assessment.
- Monitor wallet-to-wallet transfers with no apparent commercial purpose.

**What to do as the analyst**

- Test document authenticity and liveness signals, not just document presence.
- Review agent-level metrics as a distinct risk surface.
- Look for shared technical fingerprints across supposedly unrelated onboardings.

**Sources**

- [FCA - Publications](https://www.fca.org.uk/publications)
- [EBA - European Banking Authority](https://www.eba.europa.eu/)

---

# Corporate structures

## Professional enablers and TCSP abuse

*Also called: gatekeepers, professional facilitators*  ·  id `professional-enablers`

Lawyers, accountants, formation agents and trust or company service providers lend legitimacy and technical capability to laundering. This is a standing priority in the UK National Risk Assessment, and the reason the UK is consolidating professional-body AML supervision under a single supervisor.

**How it works**

1. Client account of a law firm is used to hold or move funds with no underlying legal work.
2. Complex structures are designed specifically to defeat ownership transparency.
3. Sham loans, backdated agreements, or fabricated consultancy invoices create a paper source of funds.
4. The professional's reputation is used to reassure a bank during onboarding.
5. Advice is given on how to stay below thresholds or outside a supervisory perimeter.

**Impact on banks**

The UK National Risk Assessment repeatedly identifies professional services as a leading laundering channel, and supervision is consolidating under a single professional-services supervisor. For a bank the trap is reliance: treating a regulated intermediary's introduction as a substitute for your own CDD is the failure mode regulators criticise most often.

**Red flags**

- Funds through a client account with no corresponding legal or accounting service.
- Client introduced by an intermediary who resists direct contact between bank and client.
- Documentation that is unusually polished but unverifiable at source.
- Loan agreements between related parties at non-commercial terms.
- Professional unable or unwilling to explain the commercial rationale for a structure.

**How to spot it**

- Question funds moving through a client account with no identifiable underlying legal or accounting matter.
- Flag intermediaries who resist direct contact between the bank and the underlying client.
- Check loan and consultancy agreements between connected parties for non-commercial terms.
- Verify the professional's actual supervisory status and standing, not just their claim.
- Look for unusually polished documentation that cannot be verified at source.

**What to do as the analyst**

- Do not treat a regulated intermediary's word as a substitute for your own CDD.
- Ask what the underlying legal matter is when funds pass through a client account.
- Verify the professional's actual supervisory status and standing.

**Sources**

- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)
- [Money Laundering Regulations 2017 (as amended)](https://www.legislation.gov.uk/uksi/2017/692/contents)

## Shell and shelf companies

*Also called: front companies, letterbox companies, corporate opacity*  ·  id `shell-companies`

Legal persons with no genuine trading substance are used to hold accounts, own assets, and stand between the criminal and the money. A shell is created for the purpose; a shelf is aged on the register to look established. UK reform under ECCTA and the EU beneficial ownership regime both target exactly this.

**How it works**

1. Incorporation in a jurisdiction with weak verification, or in bulk by a formation agent.
2. Nominee directors and shareholders obscure the true controller.
3. Layers of companies across jurisdictions defeat a single-hop ownership check.
4. The company opens bank accounts and receives payments with no matching commercial activity.
5. Ownership is refreshed or the company is dissolved before scrutiny lands.

**Impact on banks**

Corporate opacity underlies most large laundering cases, and UK/EU reform has moved the expectation from 'we collected an ownership form' to 'we verified it'. With Companies House identity verification and the EU beneficial ownership regime, a bank that cannot evidence who controls its corporate customers is now visibly behind the standard.

**Red flags**

- Registered address shared with hundreds of other companies.
- Directors resident far from the company's claimed operations, or serving on dozens of boards.
- Incorporated very recently but transacting at high value immediately.
- No employees, no website, no filed accounts, or persistently dormant filings.
- Ownership chain terminating in a secrecy jurisdiction or a bearer-share structure.
- Company name closely mimics an established brand.
- Formation agent is the only real point of contact.

**How to spot it**

- Flag registered addresses shared by an abnormally high number of companies.
- Alert on companies transacting at high value within weeks of incorporation.
- Check for directors holding dozens of appointments, or resident far from claimed operations.
- Compare filed accounts and dormant status against actual account turnover.
- Trace ownership to a natural person and record explicitly where and why the chain terminates.
- Flag name similarity to established brands at onboarding.

**What to do as the analyst**

- Trace ownership to a natural person; record where the chain went cold and why.
- Cross-check the registered address for mass-registration.
- Compare filed accounts against transaction volumes seen on the account.
- Check whether Companies House identity verification has actually been completed for filers.

**Sources**

- [Economic Crime and Corporate Transparency Act 2023](https://www.legislation.gov.uk/ukpga/2023/56/contents)
- [Companies House - GOV.UK](https://www.gov.uk/government/organisations/companies-house)

---

# Corruption

## PEP, kleptocracy and grand corruption proceeds

*Also called: state capture, political corruption laundering*  ·  id `pep-kleptocracy`

Proceeds of bribery, embezzlement or state capture moved abroad by politically exposed persons, their families and close associates. PEP status is not itself suspicion - it is a risk factor requiring enhanced measures and, critically, source-of-wealth evidence rather than only source of funds.

**How it works**

1. Public funds diverted through inflated state contracts or fictitious suppliers.
2. Proceeds routed via family members and close associates to avoid direct PEP matching.
3. Offshore companies and trusts hold the assets.
4. Integration through property, luxury goods, art, private education and professional fees.
5. Legitimising narrative built through consultancy income or a family business.

**Impact on banks**

PEP relationships are where source-of-wealth evidencing is tested hardest, and failures are reputationally severe because they attract press and parliamentary attention. Private banking and wealth management carry most of this exposure; the standard is a documented, career-length wealth narrative, not a transaction-level explanation.

**Red flags**

- Wealth accumulated rapidly during or shortly after public office.
- Source of wealth explained only by a business that cannot be evidenced.
- Payments from state-owned entities or government contracts into personal structures.
- Family members holding assets disproportionate to their own careers.
- Reluctance to identify the connection to the public official.
- Adverse media alleging corruption, even without charge or conviction.

**How to spot it**

- Evidence source of wealth across a career, not source of funds for one transaction.
- Screen close associates and family members, not only the named official.
- Flag payments from state-owned entities or government contracts into personal structures.
- Test whether declared role and remuneration plausibly support observed assets.
- Treat credible adverse media as a risk input requiring a documented decision either way.
- Record the rationale for retaining the relationship as carefully as for exiting it.

**What to do as the analyst**

- Evidence source of wealth over a career, not just source of funds for one transaction.
- Screen close associates and family, not only the PEP.
- Treat credible adverse media as a risk input requiring assessment and a documented decision.
- Record the rationale for continuing the relationship as carefully as for exiting it.

**Sources**

- [Money Laundering Regulations 2017 (as amended)](https://www.legislation.gov.uk/uksi/2017/692/contents)
- [FATF - Publications](https://www.fatf-gafi.org/en/publications.html)

---

# Exploitation

## Human trafficking and modern slavery finance

*Also called: labour exploitation finance, MSHT*  ·  id `human-trafficking`

Exploitation generates cash and leaves distinctive financial fingerprints: controlled accounts, shared addresses, wages recycled back to the controller. Financial institutions are often the only party positioned to see the pattern, which is why FIU red-flag guidance targets this specifically.

**How it works**

1. Accounts opened in victims' names but controlled by the exploiter.
2. Wages paid in, then immediately withdrawn or transferred to the controller.
3. Multiple accounts sharing an address, phone number or device.
4. Deductions for 'accommodation' and 'transport' strip the victim's earnings.
5. Proceeds laundered through cash-intensive businesses such as car washes or nail bars.

**Impact on banks**

Banks are frequently the only institution positioned to see the financial pattern, and UK reviews following major prosecutions have criticised underuse of branch-level observation. Exposure is both regulatory and reputational, and it intersects with modern slavery reporting obligations.

**Red flags**

- Several unrelated customers sharing one address or contact number.
- Salary credits from one employer across many accounts, each swept the same day.
- Customer accompanied and prompted during branch interactions.
- Limited language ability combined with a third party controlling the conversation.
- Benefit payments across multiple accounts routed to a single beneficiary.
- Low-value transactions at locations far from the stated home address.

**How to spot it**

- Cluster the book by address, phone number and device - this is invisible per-account.
- Flag salary credits from one employer across many accounts, each swept the same day.
- Record instances where a third party accompanies and answers for a customer at onboarding.
- Look for benefit payments across multiple accounts routing to a single beneficiary.
- Flag transactions at locations far from the stated home address.
- Route through vulnerability protocols alongside the SAR - and never tip off.

**What to do as the analyst**

- Cluster the book by address, phone and device - the pattern only shows in aggregate.
- Treat safeguarding as a parallel obligation to the SAR.
- Do not tip off; report through the proper channel and follow internal vulnerability protocols.

**Sources**

- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)
- [Europol - Newsroom](https://www.europol.europa.eu/media-press/newsroom)

---

# Fraud & predicate offences

## Authorised push payment (APP) fraud

*Also called: APP scam, bank transfer fraud*  ·  id `app-fraud`

The victim is deceived into authorising the payment themselves, which is what makes it hard to stop: the payment carries genuine customer authentication. In the UK this sits at the centre of reimbursement policy, and the proceeds almost always land in mule accounts, tying this typology directly to KYC quality at onboarding.

**How it works**

1. Social engineering: impersonation of a bank, police, HMRC, a solicitor or a supplier.
2. The victim is pressured into moving funds to a 'safe account' or paying a fake invoice.
3. Payment is authorised by the victim through normal authentication.
4. Funds are received by a mule account and dispersed within minutes to hours.
5. Onward layering through crypto, overseas transfer, or high-value goods.

**Impact on banks**

Under UK reimbursement rules the cost of APP fraud is shared between sending and receiving firms, which makes inbound detection a balance-sheet issue as well as a compliance one. Receiving banks are expected to spot mule accounts before the money leaves, and the regulator publishes firm-level performance data, so this is reputational too.

**Red flags**

- Beneficiary account is new and receiving its first large credit.
- Payment reference inconsistent with the beneficiary name (before/against Confirmation of Payee).
- Victim-side: unusual payment to a new payee, out of pattern in size and urgency.
- Beneficiary immediately disperses to multiple onward accounts.
- Multiple unrelated payers crediting the same beneficiary in a short window.

**How to spot it**

- Prioritise first-credit-on-new-account alerts for immediate review, not batch review.
- Treat Confirmation of Payee mismatches as a KYC signal and retain them for pattern analysis.
- Flag beneficiaries receiving credits from multiple unrelated payers in a short window.
- On the sending side, alert on a new payee paid an unusually large amount out of pattern.
- Watch for immediate onward dispersal or cash withdrawal after an inbound credit.

**What to do as the analyst**

- Treat inbound-side detection as your responsibility, not only outbound.
- Prioritise first-credit-on-new-account alerts.
- Check Confirmation of Payee mismatches as a KYC signal, not just a payments one.

**Sources**

- [FCA - News and enforcement](https://www.fca.org.uk/news)
- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)

## Business email compromise and invoice redirection

*Also called: BEC, mandate fraud, CEO fraud*  ·  id `bec-invoice`

An attacker compromises or spoofs business email to redirect a genuine payment to an account they control. The payment is authorised by a real employee against what looks like a real invoice, so the fraud surfaces only when the true supplier chases. Proceeds route through mule and corporate accounts.

**How it works**

1. Reconnaissance of supplier relationships via compromised mailboxes.
2. Interception or spoofing of an invoice, changing only the bank details.
3. Urgency and authority cues pressure staff to bypass verification.
4. Funds land in a corporate-looking account, often named similarly to the real supplier.
5. Rapid dispersal onward before the discrepancy is noticed.

**Impact on banks**

BEC is among the highest-value fraud categories by loss, and the receiving bank is where it can be stopped. Recovery windows are measured in hours, so detection latency is the controlling variable. Corporate banking onboarding is the exposure point.

**Red flags**

- Newly opened business account named similarly to an established company.
- Large first credit from an unrelated corporate payer.
- Beneficiary account jurisdiction differs from the supplier's known location.
- Immediate onward transfer or cash withdrawal after credit.
- Account signatory profile inconsistent with the claimed trading activity.

**How to spot it**

- Flag new business accounts whose name closely resembles an established company.
- Alert on a large first credit from an unrelated corporate payer into a young account.
- Check beneficiary jurisdiction against the supplier's known operating location.
- Escalate immediate onward transfer or cash withdrawal after a large corporate credit.
- Compare signatory profile against the claimed trading activity.

**What to do as the analyst**

- Scrutinise business accounts whose name closely resembles an established firm.
- Treat first-large-credit-then-dispersal on a young corporate account as high priority.
- Preserve the payment chain quickly - recovery windows are hours, not days.

**Sources**

- [Europol - Newsroom](https://www.europol.europa.eu/media-press/newsroom)
- [NCA - News](https://www.nationalcrimeagency.gov.uk/news)

## Bust-out fraud

*Also called: credit bust-out, sleeper fraud*  ·  id `bust-out`

A customer or business builds a good credit record over months, obtains rising limits, then draws everything at once and disappears. The long, well-behaved build-up phase is what defeats monitoring tuned to immediate anomalies.

**How it works**

1. Account or facility opened, sometimes with a synthetic or stolen identity.
2. Deliberately good conduct over months to earn limit increases.
3. Additional facilities obtained across multiple institutions in parallel.
4. Payments made with cheques or transfers that later fail, temporarily inflating available credit.
5. Simultaneous maximum drawdown across all facilities, then abandonment.

**Impact on banks**

Losses are concentrated and sudden, and the long well-behaved build-up defeats monitoring tuned to immediate anomalies. Credit and financial crime teams often own different halves of the signal, which is why it is missed - the detection requires joining them.

**Red flags**

- Sudden full utilisation after a long period of modest, tidy use.
- Payments from newly appearing third-party sources shortly before drawdown.
- Multiple applications across institutions in a short window.
- Contact details changed shortly before the drawdown.
- Business showing turnover with no corresponding supplier or wage payments.

**How to spot it**

- Monitor for behaviour change against the customer's own baseline, not absolute thresholds.
- Flag sudden full utilisation after a long period of modest, tidy use.
- Alert on failed or reversed inbound payments shortly followed by drawdown.
- Watch for clustered limit-increase requests across the market via bureau data.
- Flag contact-detail changes shortly before significant drawdown.
- Question business turnover with no corresponding supplier or wage payments.

**What to do as the analyst**

- Monitor for behaviour change, not only for absolute thresholds.
- Flag limit-increase requests clustered across the market.
- Treat failed inbound payments followed by drawdown as urgent.

**Sources**

- [FCA - News](https://www.fca.org.uk/news)
- [Europol - Newsroom](https://www.europol.europa.eu/media-press/newsroom)

## Romance and investment fraud (incl. 'pig butchering')

*Also called: pig butchering, sha zhu pan, confidence fraud*  ·  id `romance-investment`

A long-term relationship is built with the victim before a fake investment - usually crypto - is introduced. Victims often make many payments over months and may defend the 'investment' when challenged. Scam operations are frequently run from compounds using trafficked labour, so this also carries a human exploitation dimension.

**How it works**

1. Contact through dating apps, social media, or an apparently misdirected message.
2. Weeks or months of trust-building before money is mentioned.
3. Victim is directed to a convincing but fake trading platform showing gains.
4. Small withdrawals are permitted early to build confidence.
5. Escalating deposits, then 'tax' or 'release fee' demands, then loss of contact.

**Impact on banks**

These frauds produce repeat losses from a single customer over months and often involve vulnerable people, so they engage consumer duty and vulnerability obligations alongside financial crime ones. Many scam operations run on trafficked labour, which adds a human-rights dimension to the bank's exposure.

**Red flags**

- Older or recently bereaved customer making escalating payments to a crypto exchange.
- Customer's explanation matches a coached script, or they resist branch discussion.
- New payee added then paid repeatedly at increasing amounts.
- Borrowing, pension release, or asset sale to fund 'investment'.
- Payments to a platform with no regulatory authorisation.

**How to spot it**

- Flag escalating payments to a newly added payee, especially toward crypto exchanges.
- Alert on borrowing, pension release or asset sale immediately preceding transfers.
- Check whether the destination platform holds any regulatory authorisation.
- Treat customer resistance to branch discussion as a signal, not a resolution.
- Build intervention around evidence - expect the customer to deny and defend the scheme.

**What to do as the analyst**

- Treat this as a vulnerability issue alongside the financial crime issue.
- Check whether the platform is authorised before accepting the customer's account of it.
- Expect denial - build intervention around evidence rather than the customer's agreement.

**Sources**

- [FCA - News and warnings](https://www.fca.org.uk/news)
- [Europol - Newsroom](https://www.europol.europa.eu/media-press/newsroom)

---

# Integration

## Gambling and gaming laundering

*Also called: casino laundering, in-game laundering*  ·  id `gambling`

Gambling converts cash into an apparently legitimate win, and betting markets allow value to be transferred between colluding parties at low cost. Online accounts, e-sports and in-game economies have widened the channel considerably.

**How it works**

1. Cash buys chips or credits; minimal play; cash-out requested as a cheque or transfer.
2. Matched betting between colluding accounts moves value with small, predictable loss.
3. Winning tickets purchased at a premium from genuine winners.
4. Account-to-account transfers within a gambling platform used as a payment rail.
5. In-game items or currency bought and resold on secondary markets.

**Impact on banks**

Casinos and gambling operators are regulated AML entities in their own right, and Australian enforcement has produced penalties in the hundreds of millions. For banks the exposure is both banking these operators and processing customer transactions whose merchant category may not reflect actual activity.

**Red flags**

- Large deposits with minimal actual play before withdrawal.
- Consistent low-margin betting across paired accounts.
- Withdrawal requested to a different payment method or party than the deposit.
- Customer income cannot support the deposit volume.
- Frequent deposits and withdrawals with near-neutral net position.

**How to spot it**

- Measure deposit-to-play ratio - large deposits with minimal play then withdrawal is the core signal.
- Require withdrawals to return to the original funding instrument.
- Look for account pairs with mirrored or matched betting patterns and near-neutral net position.
- Test merchant category and payment narrative against the underlying activity.
- Compare deposit volume against declared customer income.

**What to do as the analyst**

- Focus on deposit-to-play ratio rather than volume alone.
- Insist that withdrawals return to the original funding instrument.
- Look for account pairs with mirrored betting patterns.

**Sources**

- [FATF - Publications](https://www.fatf-gafi.org/en/publications.html)
- [HM Treasury - GOV.UK](https://www.gov.uk/government/organisations/hm-treasury)

## Real estate laundering

*Also called: property laundering*  ·  id `real-estate`

Property absorbs large sums in a single transaction, holds value, and is socially unremarkable to own. It is a favoured integration route, particularly for foreign proceeds entering the UK and EU markets, and is the target of overseas-entity registration and unexplained wealth order powers.

**How it works**

1. Purchase through a company or trust, often overseas, rather than in a personal name.
2. Funding via loans from connected parties, or from a lawyer's client account.
3. Deliberate over- or under-valuation to move value between buyer and seller.
4. Renovation costs inflated to absorb further cash.
5. Rapid resale ('flipping') or refinancing to convert the asset back to clean funds.

**Impact on banks**

Property is the main integration route for foreign proceeds entering the UK and EU, and the register of overseas entities plus unexplained wealth order powers mean banks and conveyancers are expected to evidence source of funds properly. Mortgage and private banking teams carry the exposure.

**Red flags**

- Buyer is an overseas entity whose beneficial owner cannot be established.
- Purchase price materially out of line with comparable properties.
- Funds arriving from multiple third parties or unrelated jurisdictions.
- Cash purchase with no mortgage where the buyer's profile suggests financing would be normal.
- Buyer indifferent to price, condition, or rental yield.
- Quick resale at a materially different price without works.

**How to spot it**

- Establish the beneficial owner of any corporate buyer before assessing the funds.
- Compare purchase price against comparable local transactions; flag material divergence.
- Reconcile source-of-funds documents to the actual payment path, not just a closing balance.
- Flag funds arriving from multiple third parties or unrelated jurisdictions.
- Check overseas entity registration status where the regime requires it.
- Query rapid resale at materially different value without works.

**What to do as the analyst**

- Establish the beneficial owner of any corporate buyer before the funds question.
- Reconcile source of funds documents to the actual payment path, not just to a bank statement.
- Check the overseas entity's registration status where the regime requires it.

**Sources**

- [Economic Crime (Transparency and Enforcement) Act 2022](https://www.legislation.gov.uk/ukpga/2022/10/contents)
- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)

---

# Layering

## Money mule networks

*Also called: mule accounts, money transfer agents (illicit)*  ·  id `money-mules`

Third parties let their personal accounts be used to receive and forward criminal proceeds, usually fraud proceeds. Mules break the audit trail between victim and criminal. Recruitment increasingly runs through social media and targets students, new migrants and people in financial distress - a population that overlaps heavily with normal new-to-bank onboarding.

**How it works**

1. Recruitment via social media, messaging apps, or fake job adverts promising easy commission.
2. The mule opens or repurposes a personal account, sometimes handing over credentials outright.
3. Fraud proceeds land in the mule account, often from several victims.
4. Funds are forwarded within hours to a second-tier mule, crypto exchange, or overseas account.
5. The account is abandoned or the mule is 'burned' once flagged.

**Impact on banks**

Mule accounts are the single largest driver of inbound fraud-proceeds risk for retail banks and e-money firms, and they sit squarely in your onboarding and monitoring controls. Reimbursement regimes have shifted cost toward receiving institutions, so a weak mule detection capability is now a direct financial loss, not just a regulatory one.

**Red flags**

- New account, minimal profile, sudden inbound credits from unrelated third parties.
- Inbound and outbound near-identical amounts within hours ('pass-through' or flow-through).
- Balance repeatedly returns to near zero.
- Customer is young or a student with credits far exceeding declared income.
- Device or IP shared across multiple otherwise unconnected customers.
- Account opened shortly before first suspicious credit.
- Customer cannot explain the source or the payer when asked.

**How to spot it**

- Alert on first large credit into a recently opened account from an unrelated third party.
- Measure funds residency - inbound and near-identical outbound within hours is the core signal.
- Flag accounts whose balance repeatedly returns to near zero after activity.
- Run device, IP and phone-number linkage across the customer base to find rings.
- Compare credit volume against declared income, especially for students and new-to-bank customers.
- Cluster on shared beneficiary details across nominally unconnected accounts.

**What to do as the analyst**

- Look at velocity and residency of funds, not just amount.
- Run device/IP/phone-number linkage across the customer base.
- Check for shared beneficiary details across supposedly unrelated accounts.
- Remember the mule may be a victim of coercion - consider vulnerability alongside the SAR.

**Sources**

- [Europol - Newsroom (European Money Mule Action / EMMA reporting)](https://www.europol.europa.eu/media-press/newsroom)
- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)

---

# Placement

## Cash-intensive business co-mingling

*Also called: front business laundering, commingling*  ·  id `cash-intensive`

Criminal cash is mixed with the genuine takings of a business that legitimately handles cash, so the deposit looks like normal trade. Classic vehicles are car washes, barbers, takeaways, nail bars, vending and small retail. UK NRA work has repeatedly identified cash-based laundering as a leading domestic risk.

**How it works**

1. A cash-generating business is acquired or established, sometimes with a real customer base.
2. Criminal cash is added to daily takings before banking.
3. Turnover is inflated in the accounts to justify the deposits, and tax is paid on the excess.
4. Profits are extracted as dividends, wages, or loans to connected parties.
5. Multiple such businesses may be run in parallel under different owners.

**Impact on banks**

Cash-based laundering is consistently identified as a leading domestic risk in the UK National Risk Assessment, and it is the typology behind the largest UK AML enforcement action to date. For banks the exposure is SME business banking, where onboarding assumptions are rarely refreshed against actual behaviour.

**Red flags**

- Takings materially above what floor space, staffing or opening hours could plausibly generate.
- Deposits with no seasonal variation, or unchanged through periods when trade should dip.
- Very low card-to-cash ratio compared with sector norms.
- Wages paid to staff who cannot be evidenced, or minimal supplier payments.
- Business acquired for cash by an owner with no sector experience.
- Deposits in worn, banded, or unusually denominated notes.

**How to spot it**

- Benchmark card-to-cash ratio against sector norms - this is the single strongest test.
- Compare banked takings against premises size, staffing and opening hours.
- Flag deposits that show no seasonal variation where the sector should show one.
- Reconcile declared turnover against filed accounts and VAT position.
- Check for minimal supplier or wage payments alongside high takings.
- Refresh expected-turnover assumptions periodically rather than only at onboarding.

**What to do as the analyst**

- Benchmark card-versus-cash ratio against the sector - this is one of the strongest single tests.
- Compare declared turnover to filed accounts and to VAT position.
- Consider the premises: a car wash banking six figures monthly deserves a site question.

**Sources**

- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)
- [HM Treasury - GOV.UK (National Risk Assessment)](https://www.gov.uk/government/organisations/hm-treasury)

## Structuring / smurfing

*Also called: smurfing, breaking down, cash structuring*  ·  id `structuring`

Cash is broken into amounts small enough to sit below a reporting or scrutiny threshold, then deposited across many accounts, branches, people or days. The defining feature is deliberate threshold avoidance, which is itself the offence in many regimes regardless of whether the underlying funds are dirty.

**How it works**

1. A total sum is divided into tranches below the relevant reporting or internal review threshold.
2. Deposits are spread across multiple branches, ATMs, or cash-in machines to avoid any single teller seeing a pattern.
3. Multiple individuals ('smurfs') are recruited to make deposits in their own names.
4. Funds are consolidated upward into a single account once placed.
5. Increasingly done through cash-accepting ATMs and retail agents rather than branches.

**Impact on banks**

Cash structuring is the classic placement risk for any bank with a branch or ATM network, and it is the failure regulators find easiest to evidence after the fact because the pattern sits in your own data. Post-NatWest, UK firms are also exposed to the argument that ignoring an obvious aggregate pattern is a criminal-standard failure, not just a civil one.

**Red flags**

- Repeated deposits just under a round threshold (e.g. repeated GBP 9,000s).
- Multiple deposits same day at different branches or ATMs.
- Several unrelated individuals depositing into one account in sequence.
- Customer asks staff what the reporting threshold is, or splits a transaction when told.
- Deposit pattern inconsistent with the customer's stated income or business takings.
- Immediate onward transfer of the consolidated balance.

**How to spot it**

- Aggregate deposits by customer by rolling day/week, not per transaction - structuring is invisible at transaction level.
- Alert on repeated deposits landing just under a reporting or internal review threshold.
- Flag same-day deposits made at three or more distinct branches or ATMs.
- Compare cash-in totals against declared income or expected turnover captured at onboarding.
- Watch for consolidation: several accounts feeding one, then a single onward transfer.
- Check whether the deposit locations cluster far from the customer's registered address.

**What to do as the analyst**

- Aggregate by customer, by day and by counterparty - not by single transaction.
- Check whether deposit locations form a geographic cluster inconsistent with the customer's address.
- Test the pattern against declared income and expected turnover captured at onboarding.

**Sources**

- [NCA - Money laundering and illicit finance](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance)
- [JMLSG - Current guidance](https://www.jmlsg.org.uk/guidance/current-guidance/)

---

# Process

## SARs, DAML and the reporting mechanics (process explainer)

*Also called: suspicious activity report, defence against money laundering, consent regime*  ·  id `sars-daml`

Not a typology, but the machinery every typology ends in. Under POCA a person in the regulated sector who knows or suspects money laundering must report to the NCA. A DAML request seeks a defence against committing a principal laundering offence by proceeding with a transaction. Tipping off is a separate criminal offence.

**How it works**

1. Internal escalation: staff report suspicion to the nominated officer (MLRO).
2. The MLRO decides whether the suspicion meets the threshold for an external report.
3. A SAR is submitted to the UKFIU at the NCA.
4. Where the firm wants to proceed with an act that might be a principal offence, it requests a DAML.
5. Statutory notice and moratorium periods govern how long the firm must wait.
6. Tipping off the customer, or prejudicing an investigation, is a separate offence.

**Impact on banks**

SAR quality directly affects law enforcement outcomes, and the UKFIU has been explicit that poor narratives and missing glossary codes reduce intelligence value. Failure to report, and tipping off, are criminal offences for individuals as well as firms - this is personal liability, not just institutional.

**Red flags**

- Suspicion is knowledge or suspicion - it is a lower bar than proof, and does not require certainty.
- Do not delay a report to gather more evidence than the threshold requires.
- A poor-quality SAR with no glossary code or clear narrative reduces its intelligence value.

**How to spot it**

- Report on suspicion - a lower bar than proof. Do not delay to gather more than the threshold requires.
- Write the narrative so a reader outside your firm can follow it without access to your systems.
- Apply current UKFIU glossary codes - they determine how the report is routed.
- Track DAML statutory notice and moratorium periods against your action dates.
- Record your reasoning where you decide not to report, as carefully as where you do.
- Manage the customer relationship carefully - never disclose that a report has been made.

**What to do as the analyst**

- Write the narrative so a reader outside your firm can follow it without your systems.
- Use the current UKFIU glossary codes - they drive how the report is routed.
- Never tell the customer a report has been made; manage the relationship carefully instead.
- Record your reasoning even where you decide not to report.

**Sources**

- [NCA - Suspicious Activity Reports](https://www.nationalcrimeagency.gov.uk/what-we-do/crime-threats/money-laundering-and-illicit-finance/suspicious-activity-reports)
- [Proceeds of Crime Act 2002](https://www.legislation.gov.uk/ukpga/2002/29/contents)

---

# Sanctions

## Proliferation financing

*Also called: PF, WMD financing*  ·  id `proliferation`

Financing the acquisition of goods, technology or expertise for weapons programmes in breach of targeted sanctions. UK firms have an explicit obligation to assess proliferation financing risk, and it demands attention to what is being bought and by whom, not only to whether a name is listed.

**How it works**

1. Front companies in third countries procure controlled or dual-use goods.
2. End-user certificates falsified to show a civilian purpose.
3. Payments routed through several jurisdictions to obscure origin.
4. Overseas representatives operate under diplomatic or commercial cover.
5. IT contracting and crypto theft used to generate revenue for sanctioned programmes.

**Impact on banks**

UK firms have an explicit obligation to assess proliferation financing risk in their business-wide risk assessment - it is a named requirement, not an optional extension of sanctions work. The end use is a weapons programme, so escalation is immediate and the tolerance is zero.

**Red flags**

- Dual-use goods shipped to an end user with no plausible civilian need.
- End-user documentation that is generic, inconsistent, or unverifiable.
- Trading company incorporated recently in a transhipment hub.
- Payment routing disproportionately complex for the transaction value.
- Remote IT workers with document inconsistencies and payment to third parties.

**How to spot it**

- Assess proliferation financing explicitly in the business-wide risk assessment and evidence it.
- Screen goods descriptions and end users, not only counterparty names.
- Flag dual-use goods shipped to end users with no plausible civilian need.
- Question generic or unverifiable end-user certificates.
- Flag trading companies recently incorporated in transhipment hubs.
- Check remote-worker payment instructions directing funds to unrelated third parties.

**What to do as the analyst**

- Assess proliferation financing risk explicitly in your business-wide risk assessment.
- Screen goods descriptions and end users, not only counterparty names.
- Escalate any dual-use indicator immediately - this is sanctions territory.

**Sources**

- [OFSI - GOV.UK](https://www.gov.uk/government/organisations/office-of-financial-sanctions-implementation)
- [FATF - Publications](https://www.fatf-gafi.org/en/publications.html)

## Sanctions evasion and circumvention

*Also called: sanctions busting, designation avoidance*  ·  id `sanctions-evasion`

Designated persons and entities continue to access the financial system through ownership restructuring, intermediaries and third-country routing. Since 2022 this has been the fastest-moving area of UK and EU financial crime supervision, and it carries strict-liability exposure that ordinary AML risk-based judgement does not.

**How it works**

1. Ownership diluted below the control threshold, or transferred to a non-designated proxy.
2. Trade routed through third countries that have not imposed equivalent measures.
3. New intermediary companies created to break the documentary link to the designated party.
4. Payment messages altered or stripped to conceal the true originator.
5. Use of crypto, barter, or informal value transfer to bypass correspondent rails entirely.

**Impact on banks**

Sanctions breach is strict liability - the risk-based judgement that governs AML does not apply. Exposure includes secondary sanctions and, for dollar-clearing banks, potential loss of market access. Since 2022 this has been the fastest-moving supervisory area in the UK and EU.

**Red flags**

- Ownership restructured to just under a designation threshold shortly after listing.
- Sudden appearance of a new intermediary in a previously direct trade relationship.
- Goods or payments routed via a third country with no commercial logic.
- Counterparty registered days before the transaction.
- Customer resists questions about end-user or ultimate destination.
- Dual-use or controlled goods with a civilian cover story.

**How to spot it**

- Screen on ownership and control, not name matching alone - control can exist below equity thresholds.
- Re-screen the entire book after every list change, not only at onboarding.
- Flag ownership restructured to just below a designation threshold shortly after a listing.
- Alert on new intermediaries appearing in previously direct trade relationships.
- Question goods or payments routed through third countries with no commercial logic.
- Check whether an OFSI licence is required before any action that could constitute dealing.

**What to do as the analyst**

- Check ownership and control, not only name matching - control can exist below equity thresholds.
- Re-screen the book after every list change, not only at onboarding.
- Escalate immediately: sanctions breaches are strict liability, unlike risk-based AML.
- Consider whether an OFSI licence is required before any action that could be a dealing.

**Sources**

- [OFSI - Office of Financial Sanctions Implementation (GOV.UK)](https://www.gov.uk/government/organisations/office-of-financial-sanctions-implementation)
- [The UK Sanctions List](https://www.gov.uk/government/publications/the-uk-sanctions-list)

## Shadow fleet and oil price cap evasion

*Also called: dark fleet, grey fleet*  ·  id `shadow-fleet`

Ageing tankers with opaque ownership, uncertain insurance and disabled tracking move sanctioned oil above price caps. For a KYC analyst the exposure is rarely the vessel itself - it is the shipping company, charterer, insurer, commodity trader or payment intermediary that appears as your customer.

**How it works**

1. Vessel ownership placed in single-ship companies in opaque registries.
2. AIS transponders switched off or spoofed to conceal port calls and transfers.
3. Ship-to-ship transfers at sea blend sanctioned and non-sanctioned cargo.
4. Documents falsified to misstate cargo origin.
5. Attestations of price-cap compliance provided by parties with no real visibility.
6. Insurance obtained from providers outside established markets.

**Impact on banks**

Exposure reaches banks through shipping companies, charterers, commodity traders, insurers and payment intermediaries rather than through vessels directly. Price-cap attestation regimes place a documentation burden on financial institutions, and OFSI has made clear that accepting an attestation uncritically is not compliance.

**Red flags**

- Counterparty is a newly formed single-vessel company with no trading history.
- AIS gaps that coincide with loading windows.
- Cargo origin documentation inconsistent with voyage data.
- Price attestations that are generic or unverifiable.
- Insurance from an unfamiliar provider in a non-standard jurisdiction.
- Charterer or trader incorporated shortly before the voyage.

**How to spot it**

- Screen vessel names and IMO numbers, not only corporate counterparty names.
- Flag newly formed single-vessel companies with no trading history.
- Check for AIS gaps coinciding with loading windows.
- Test cargo origin documentation against voyage data for consistency.
- Ask who provided a price attestation and on what basis - a signature is not evidence.
- Review registry and flag-state changes in the preceding 12 months.

**What to do as the analyst**

- Screen vessels and IMO numbers, not only corporate names.
- Ask who provided the attestation and on what basis - a signature alone is not evidence.
- Check registry and flag-state changes in the preceding 12 months.

**Sources**

- [OFSI - GOV.UK](https://www.gov.uk/government/organisations/office-of-financial-sanctions-implementation)
- [OFSI blog](https://ofsi.blog.gov.uk/)

---

# Terrorist financing

## Charity and NPO abuse for terrorist financing

*Also called: NPO abuse, charitable diversion*  ·  id `npo-abuse`

Charitable structures move funds to conflict zones with a humanitarian cover story, or divert a portion of genuine donations. FATF is explicit that the sector must not be treated as uniformly high risk - the obligation is targeted, risk-based measures, and over-broad de-risking is itself a recognised harm.

**How it works**

1. A charity is established, or an existing one infiltrated, to provide cover.
2. Donations collected in cash at events, so individual donors are untraceable.
3. Funds transferred to partner organisations in high-risk or conflict areas.
4. Only part of the funds is diverted, so accounts broadly reconcile.
5. Cash couriers or informal transfer used for the final leg.

**Impact on banks**

FATF is explicit that the NPO sector must not be treated as uniformly high risk, and over-broad de-risking is itself a recognised harm that supervisors will criticise. The bank's obligation is targeted, proportionate measures - which is harder than a blanket policy and needs to be evidenced.

**Red flags**

- Beneficiary organisations that cannot be verified as existing.
- Activity in a conflict zone inconsistent with the charity's registered objects.
- Large cash collections with weak record-keeping.
- Trustees with adverse media or links to designated entities.
- Rapid growth in donations without a matching fundraising campaign.

**How to spot it**

- Verify overseas partner organisations, not only the UK/EU registered charity.
- Check registration and trustee details against the relevant charity regulator.
- Flag activity in conflict zones inconsistent with the charity's registered objects.
- Question large cash collections with weak record-keeping.
- Screen trustees for adverse media and links to designated entities.
- Document why measures are proportionate - blanket exit is a supervisory risk in itself.

**What to do as the analyst**

- Apply proportionate, targeted measures - blanket de-risking of the sector is not the answer.
- Verify the overseas partner organisation, not only the UK/EU charity.
- Check registration and trustee details against the relevant charity regulator.

**Sources**

- [FATF - Publications (Recommendation 8 / NPO guidance)](https://www.fatf-gafi.org/en/publications.html)
- [GOV.UK - HM Treasury](https://www.gov.uk/government/organisations/hm-treasury)

---

# Trade & commerce

## Trade-based money laundering (TBML)

*Also called: trade washing, invoice manipulation*  ·  id `tbml`

Value is moved across borders by lying about a trade, not by moving money that looks dirty. The payment itself is a clean-looking commercial settlement; the lie sits in the invoice, the shipping documents, or whether the goods exist at all. It is attractive because trade finance volumes are enormous and each document is checked by a different party who sees only their slice.

**How it works**

1. Over- or under-invoicing: the invoice price is set above or below true market value, so value transfers to whichever side is favoured.
2. Multiple invoicing: the same shipment is invoiced repeatedly to several financiers, each of whom pays.
3. Short- or over-shipping: quantity or quality shipped does not match the documents; the gap is the laundered value.
4. Phantom shipping: no goods move at all; documents alone justify the payment.
5. Black market peso-style exchange: a broker settles obligations in two currencies, so no cross-border transfer ever appears.

**Impact on banks**

Trade finance is high-value, document-driven and split across correspondent banks, so no single institution sees the whole picture. Supervisors expect banks financing trade to test documents against economic reality, not just check they exist. Failures here are expensive because volumes are large and the paper trail makes remediation look like negligence in hindsight.

**Red flags**

- Invoice value materially out of line with public market prices for that commodity.
- Goods shipped through a jurisdiction with no commercial connection to buyer or seller.
- Trade documents amended repeatedly, especially the value or the consignee.
- Commodity described in unusually vague terms, or inconsistent unit of measure.
- Payment from a third party unrelated to the named buyer.
- Company's declared line of business does not fit the goods traded.
- Round-number invoices and same-day back-to-back settlement.
- Shipment routed via a free trade zone with no value added there.

**How to spot it**

- Compare declared unit price against a public commodity index; flag deviations beyond a set tolerance.
- Reconcile the goods description on the invoice against the counterparty's registered business activity (SIC/NACE).
- Flag amendments to letters of credit that change value, quantity or consignee more than once.
- Check the routing: shipments through a country with no commercial connection to buyer or seller.
- Look for third-party payers settling a trade they are not party to.
- Cross-reference vessel and IMO data against the claimed voyage where shipping documents are provided.

**What to do as the analyst**

- Compare unit price against a public commodity index; document the comparison.
- Check the counterparty's stated SIC/NACE activity against the goods on the invoice.
- Look for third-party payers and beneficial owners common to both sides of the trade.
- Confirm the vessel/route actually exists and calls where the documents claim.

**Sources**

- [FATF - Publications (Methods & Trends, incl. TBML)](https://www.fatf-gafi.org/en/publications.html)
- [Wolfsberg Group - Trade Finance Principles & resources](https://wolfsberg-group.org/resources)

---

# Virtual assets

## Crypto laundering and chain-hopping

*Also called: virtual asset laundering, cross-chain laundering*  ·  id `crypto-laundering`

Value is moved onto a blockchain, obfuscated, then cashed out. The ledger is public, which helps investigators, so launderers focus on breaking the link between addresses and on exiting through weakly supervised venues. The EU Travel Rule extension and MiCA, and the UK's move to bring cryptoasset firms into FSMA authorisation, are the regulatory responses.

**How it works**

1. Placement by buying crypto with fraud or drug proceeds, often via mule-funded accounts.
2. Chain-hopping: swapping between assets and across blockchains via bridges to break tracing.
3. Use of decentralised exchanges and swap services that perform no customer due diligence.
4. Layering through mixers, privacy coins, or large numbers of intermediate addresses ('peel chains').
5. Cash-out via an exchange in a weak-supervision jurisdiction, a P2P trader, or a crypto ATM.

**Impact on banks**

With cryptoasset firms moving into full FSMA authorisation in the UK and MiCA plus the Travel Rule applying in the EU, crypto exposure is now a supervised activity rather than an emerging risk. Banks serving crypto businesses inherit their customers' controls, and blockchain analytics means exposure is demonstrable after the fact - which cuts both ways.

**Red flags**

- Customer's fiat account funds a crypto exchange immediately after third-party credits.
- Exposure to mixers, sanctioned addresses, or darknet markets in blockchain analytics.
- Rapid movement across several chains with no economic purpose.
- Use of an exchange with no meaningful KYC, or a VASP not registered where required.
- Transfers to unhosted wallets that then fragment immediately.
- Customer's crypto activity is far out of line with declared income or investment profile.

**How to spot it**

- Treat the fiat on-ramp and off-ramp as the control point - that is where you have visibility.
- Score blockchain analytics exposure to mixers, darknet markets and designated addresses; record hop distance.
- Verify the counterparty VASP is registered or authorised in its own jurisdiction.
- Flag fiat accounts funding exchanges immediately after third-party credits.
- Record Travel Rule originator/beneficiary data completeness as a risk signal.
- Compare crypto activity against declared income and investment profile.

**What to do as the analyst**

- Treat the fiat on-ramp and off-ramp as your control point - that is where you have visibility.
- Check whether the counterparty VASP is registered/authorised in its own jurisdiction.
- Record Travel Rule originator/beneficiary data completeness as a risk signal.

**Sources**

- [Chainalysis - Research reports (annual Crypto Crime Report)](https://www.chainalysis.com/reports/)
- [FCA - News](https://www.fca.org.uk/news)

## Mixers, tumblers and privacy coins

*Also called: coin mixing, anonymity-enhancing technologies*  ·  id `mixers`

Services and assets designed to sever the link between source and destination on a public ledger. Some have been sanctioned outright, which turns their use into a sanctions exposure question as well as an AML one - a distinction that matters for how you escalate.

**How it works**

1. Deposits from many users are pooled and redistributed, breaking one-to-one traceability.
2. Privacy coins conceal amounts, addresses, or both at protocol level.
3. CoinJoin-style collaborative transactions blend inputs from multiple parties.
4. Output is withdrawn in varied amounts and delays to defeat timing correlation.

**Impact on banks**

Since OFAC designated a major mixing service, mixer exposure stopped being purely an AML risk score and became a potential sanctions breach - which is strict liability. Firms need a documented, consistent policy on direct versus indirect exposure, because inconsistent case-by-case decisions are indefensible under supervisory review.

**Red flags**

- Any direct or one-hop exposure to a designated mixing service.
- Funds arriving from a mixer immediately before an attempted fiat withdrawal.
- Customer explanation for privacy-coin use that does not fit their profile.
- Structured withdrawals in irregular amounts shortly after a mixing event.

**How to spot it**

- Screen for direct exposure to designated mixing services and escalate immediately as sanctions, not AML.
- Record hop distance from the mixer rather than a binary exposed/not-exposed flag.
- Apply a documented threshold for indirect exposure and apply it consistently.
- Flag funds arriving from a mixer shortly before a fiat withdrawal attempt.
- Question privacy-coin activity that does not fit the customer's stated profile.

**What to do as the analyst**

- Separate the AML question from the sanctions question - a sanctioned mixer is a designation issue.
- Document hop distance to the mixer, not just the fact of exposure.
- Escalate direct exposure; risk-assess indirect exposure rather than auto-exiting.

**Sources**

- [OFAC - Recent actions](https://ofac.treasury.gov/recent-actions)
- [Chainalysis - Research reports](https://www.chainalysis.com/reports/)
