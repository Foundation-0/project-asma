# Pilot 001: data-use disposition

**Checked:** 2026-10-25; Gate 0 execution hosts recorded 2026-11-05 (initial and Q1
update). **Scope:** the selected discovery reconstruction, with
no persistent source data, patient-level output or outside participant linkage.
This records source terms, project choices and unresolved facts separately.
It does not declare every public dataset unrestricted or make an institutional
review determination.

**Selected purpose:** independent, noncommercial research-method reconstruction
by a private, unaffiliated individual on his own hardware in Canada.

**Execution hosts (Gate 0, 2026-11-05).**
- **Study data (Dropbox matrix, MMC workbooks, fitting):** the owner's personal
  MacBook (macOS), physically in Canada (Q1 update, verbatim: "My MacBook is in
  Canada"; [issue #31](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662169564)).
- **Not for study data:** the Grok Bot team's shared cloud computer. Its only
  recorded location evidence is an AWS us-east-1 outbound address (Ashburn,
  Virginia, US), which is not a Canadian processing context. That host is for
  **CI and dry runs on artificial inputs only** (synthetic fixtures, mocked
  acquisition, registry checks).

The conditional Canadian assessment below applies to the MacBook host. It is
**not legal advice** and **no outside legal review** has occurred. Commercial/product
uses are outside this phase and require a new use assessment. This is a prospective
project choice, not a claim about an existing institution or a change to third-party
license terms.

**Decision:** select the case-specific Canadian research fair-dealing assessment
below as a **conditional analysis-use route** for the author Dropbox member on
the MacBook host when the conditions in
[Assessment for owner MacBook in Canada](#assessment-for-owner-macbook-in-canada-gate-0-q1-update-2026-11-05)
are met. This is not a discovered license grant or an automatic legal clearance.
Methods and software preparation can continue on any host with artificial inputs;
research fitting on study values waits on the MacBook route, attestation and preflight.
External outreach stays on hold.

## Input-specific decisions

| Input | Evidence and applicable scope | Disposition for the selected reconstruction |
| --- | --- | --- |
| Author Dropbox discovery matrix | Article XML S27 expressly offers processed data for public download; the exact member is now hash/CRC-pinned. No archive-specific reuse grant was located in its README, author repository, ProTrack or the targeted follow-up search. | Access, identity and source inspection are established. Use the conditional Canadian research fair-dealing assessment below for the proposed narrow analysis, subject to actual applicability. Do not inherit another release's license or redistribute the matrix. |
| NLM MMC1 clinical and MMC4 panel/membership workbooks | The [article-version record](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.json) identifies `CC BY-NC-ND` and explicitly associates these two media files. The article specifies version 4.0. No separate workbook-specific notice was discovered. | Use the article-associated terms conservatively. Private noncommercial adaptation is permitted by the license; the selected phase is noncommercial and must remain so to rely on this license. Retain attribution. Do not redistribute transformed source tables, linkage or score rows. Numerical score columns are unnecessary for this reconstruction. |
| Author R scripts/helper/workspaces | No explicit repository code license or recovered helper/workspace grant is established. | Remove this implementation dependency: write original code from the documented methods and parameter facts; do not copy or run the author scripts or source unknown workspaces. This resolves a route forward without inventing a code license. |
| R and model packages | Published source releases and declared GPL/Apache notices were inspected in the [runtime record](../registries/pilot-001-reconstruction-runtime.json). | Those releases and their dependencies now have an inspected, pinned [synthetic runtime](pilot-001-synthetic-validation.md). Its validation and license-notice review cover software use, not research-data clearance or a blanket license for redistributing a modified runtime. |
| PDC open proteomics | Official data-use policy states CC BY 4.0, permitting sharing and adaptation, including commercial use, with attribution. Submission policy requires deidentification and says PDC does not collect PHI. | Those rights apply to the PDC release. Its matrix identity/preprocessing gaps prevent automatic substitution for the author member. No controlled genomics is included. |
| Downstream Figshare / TCIA releases | Figshare records state CC BY 4.0. The [TCIA PTRC-HGSOC collection](https://www.cancerimagingarchive.net/collection/ptrc-hgsoc/) separately states CC BY 4.0 for its clinical release. | These are alternative releases, not a license for the selected archive. TCIA's linked clinical file is XLSX despite CSV wording; schema and equivalence to the pinned joins were not checked. Neither alternative is adopted here. |

No explicit archive license was found. A license or terms statement covering
the exact release, or a licensed byte-identical release, would be additional
evidence. If an exception applies, neither is required for that use; whether
one applies is the documented, conditional assessment below, which is the
selected route.
Repository ownership and organization names do not establish third-party rights.

## Conditional Canadian research-use assessment

Canada's [Copyright Act, section 29](https://laws-lois.justice.gc.ca/eng/acts/C-42/section-29.html)
provides fair dealing for research. In **CCH Canadian Ltd. v. Law Society of
Upper Canada, 2004 SCC 13**, paragraphs 50–60 distinguish an eligible purpose
from the separate fairness assessment and describe six factors. Paragraph 70
states that availability of a license is not relevant to whether the dealing is
fair. The judgment was inspected through the official
[WIPO judgment record](https://www.wipo.int/wipolex/en/judgments/details/3721)
and its [full judgment](https://www.wipo.int/wipolex/en/text/600136), because
direct SCC document retrieval returned HTTP 403.

The proposed narrow research is a reasonable candidate for this route if the
actual governing context supports Canadian law. The assessment is specific to
this protocol; no blanket fair-dealing status is asserted for future uses.

| CCH factor | Facts of the selected use and limits |
| --- | --- |
| Purpose | Independent, noncommercial research into a published statistical result. No clinical service, commercial model product or source-data resale is included. Research is an eligible purpose; purpose alone does not establish fairness. |
| Character | Transient processing in one isolated execution environment; no source distribution, persistent patient-level copy or model release. Only reviewed original aggregate findings and implementation are published. |
| Amount | Integrity checking copies/decompresses the **entire 18,498,831-byte member**. Modeling then selects 64 of 8,800 feature rows and the fixed 135 patients with their explicitly linked repeated measurements. The small modeled subset does not erase the full-member copying; a partial-feature download cannot verify the pinned whole member. |
| Alternatives | The exact input preserves the selected published question. PDC naming/preprocessing and downstream feature/cohort differences remain unverified alternatives, not demonstrated substitutes. This is not a claim that no alternative exists. |
| Nature | The authors deliberately released processed research data for public download. The numerical observations have a factual character; any protected compilation/annotation or other applicable rights are not assumed absent. |
| Effect | Aggregate statistical findings and original code do not supply a replacement source dataset. No evidence of a market for the exact free release was located, but market effects were not independently established. Do not convert that absence of evidence into a finding of zero effect. |

### Assessment for owner MacBook in Canada (Gate 0 Q1 update, 2026-11-05)

This subsection applies the table above to the recorded context: a **private
individual**, **unaffiliated**, doing **noncommercial** research-method
reconstruction on **his own MacBook in Canada**. It does not assert institutional
approval, a statutory licence grant, or clearance for any other host.

**Fair dealing (Copyright Act s. 29).** The pinned
[CCH judgment, WIPO full PDF](https://www.wipo.int/wipolex/en/text/600136)
(SHA-256 `3e586ac725a3ca37dcabbf4921353ef5ca87613d669b47be556627a984ea2f64` in
the evidence table below) was inspected on 2026-10-25. In that copy, **paragraph
50** states that fair dealing under s. 29 requires showing (1) the dealing was
for research or private study and (2) it was fair. **Paragraph 51** states that
“research” must be given a **large and liberal interpretation** so users’ rights
are not unduly constrained, and that research is **not limited to non-commercial
or private contexts**. This project’s purpose row in the six-factor table matches
that eligible purpose; fairness still depends on the six factors (unchanged above).
Reproduction on study values is intended to occur on a machine **physically in
Canada**. SOCAN v. Bell Canada, 2012 SCC 36, is not cited here; it was not
verified in a pinned primary copy for this record.

**TCPS 2.** The pinned
[TCPS introduction](https://ethics.gc.ca/eng/tcps2-eptc2_2022_introduction.html)
and [scope interpretations](https://ethics.gc.ca/eng/policy-politique_interpretations_scope-portee.html)
tie Tri-Council Policy Statement (TCPS 2) review obligations to eligible
institutions (for example agency-funded research or institutions that adopt the
policy). An **unaffiliated individual** is not such an institution; this record
does **not** treat TCPS 2 as binding on the owner. For completeness, the pinned
[chapter 2](https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter2-chapitre2.html)
text was re-read: **Article 2.2** exempts some research from research ethics board
(REB) review when it relies exclusively on information that is publicly available
through a legislated mechanism or is in the public domain with no reasonable
expectation of privacy, with application notes that copyright or dissemination
restrictions may still apply. **Article 2.4** exempts secondary use of
**anonymous** information when linkage or dissemination would not generate
identifiable information, with warnings that anonymity is fragile and keyed
clinical records must not be called anonymous (consistent with chapter 5 in this
file). This project does **not** assert an article 2.2 or 2.4 exemption for the
pinned clinical joins; the keyed records remain coded information under chapter 5.

**PIPEDA.** The cited
[OPC commercial-activity guidance](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/r_o_p/02_05_d_19/)
describes PIPEDA’s commercial-activity scope. The selected phase is
**noncommercial** and does not, by itself, establish a PIPEDA trigger; it also
does not establish exemption from every privacy obligation. **Provincial**
private-sector privacy statutes are **not individually assessed** here, and the
owner’s **province of residence is not recorded** — treat that as an **open**
note if provincial law might apply.

**Conclusion (Dropbox discovery matrix on the MacBook host).**

| Label | Meaning |
| --- | --- |
| **CONDITIONAL GO** | The author Dropbox member may be processed on the owner’s MacBook in Canada for this narrow reconstruction **only if** all of (a)–(c) below are satisfied. |
| **NO-GO** | If any of (a)–(c) fails, do not acquire or fit on that matrix (openly licensed inputs only). |

Conditions:

(a) **Attestation:** a dated owner attestation that the machine is in Canada, is
his own hardware, the use is noncommercial, and no institutional or funding
obligations apply (Gate 0 Q2).

(b) **macOS runtime preflight:** the checks in
[macOS runtime preflight](#macos-runtime-preflight-study-data-host) pass on that
machine before study bytes are loaded.

(c) **No row-level leakage:** nothing patient-level or source-row-level leaves
process memory, including terminal scrollback, logs, crash reports or agent-chat
output.

On these facts, the project selects a **conditional, bounded research-use
basis** for the MacBook execution route when (a)–(c) are met, rather than making
an explicit licensor grant a universal prerequisite. This is an operational
design choice, not an election of governing law. The shared cloud host is **not**
part of this route. If execution moves off the MacBook or outside Canada,
reassess before fitting; do not silently transplant a Canadian exception to
another jurisdiction.

This assessment does not authorize publication of source rows, reidentification,
commercial exploitation, redistribution of author code, or use contrary to any
applicable privacy or contractual obligations. It requires no automatic author
contact and makes no claim that an outside legal or ethics review has occurred.

## What the supplement license does and does not require

The official [CC BY-NC-ND 4.0 legal code](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en)
provides the relevant distinctions:

- **Section 2(a)(1)(B):** permits producing and reproducing adapted material for
  noncommercial purposes, but does not grant permission to share that adaptation.
  “NoDerivatives” is not a general prohibition on private computation.
- **Sections 1 and 4:** define noncommercial use and address licensed database
  rights. The actual use matters; an academic or nonprofit label is not decisive.
- **Section 2(a)(2):** preserves applicable exceptions and limitations. It does
  not establish that a particular exception applies to this project.
- **Section 3:** requires appropriate attribution when licensed material is
  shared. Public outputs here will be original code, source citations and
  reviewed aggregate findings, with no source tables or patient-level derivatives.

The CC [data-mining guidance](https://creativecommons.org/faq/#can-i-conduct-textdata-mining-on-a-cc-licensed-database),
[noncommercial guidance](https://creativecommons.org/faq/#does-my-use-violate-the-noncommercial-clause-of-the-licenses)
and [database guidance](https://creativecommons.org/faq/#which-components-of-databases-are-protected-by-copyright)
distinguish factual contents from protected arrangement and database rights.
Those distinctions narrow the assessment; they do not justify declaring the
entire Dropbox archive unrestricted. The official pages were inspected, but
direct raw retrieval failed, so no byte fingerprints are claimed for them.

## Privacy, hosting and review conditions

The source article's P67 records source institutions' IRB approvals. That does
not approve this project's secondary use or establish a broad-secondary-consent
statement; none was located in the inspected article paragraphs.

For the planned Canadian route, [TCPS 2 applicability](https://ethics.gc.ca/eng/tcps2-eptc2_2022_introduction.html)
depends on agency funding, eligible institutional auspices or adoption; a
person's nationality does not create those conditions. Whether any institutional
obligation applies to this independent phase has not been determined. The official
[scope interpretations, items 1 and 17](https://ethics.gc.ca/eng/policy-politique_interpretations_scope-portee.html)
must be read with [articles 2.2 and 2.4](https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter2-chapitre2.html):
public availability does not itself establish an exemption for deidentified
repository data. The public-domain route also requires no reasonable expectation
of privacy. [Chapter 5](https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter5-chapitre5.html)
distinguishes anonymous information, which never had associated identifiers,
from coded or anonymized information. Do not call these keyed clinical records
anonymous or assert an exemption under article 2.4.

The [Canadian privacy regulator's guidance](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/r_o_p/02_05_d_19/)
explains PIPEDA's commercial-activity scope. The selected noncommercial phase
does not establish that trigger; it does not establish an exemption from every
provincial, contractual or other privacy obligation. These checks belong in the
actual runtime/use-context preflight, not an automatic external-contact step.

For a US-governed project, [45 CFR 46.101(a)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-A/section-46.101)
defines a federal applicability scope; a public US dataset alone does not show
that every independent project falls within it. [OHRP guidance](https://www.hhs.gov/ohrp/coded-private-information-or-biospecimens-used-research.html)
distinguishes work that does not involve human subjects, where identities cannot
readily be ascertained, from research potentially exempt under
[46.104(d)(4)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-A/section-46.104).
OHRP recommends institution-designated determinations; this is not a universal
instruction to recruit an IRB for work without an institutional affiliation. Applicable institutional
policy may require its own determination. No exemption is asserted here.

Noncommercial independent research is the selected use for this phase. Actual
processing jurisdiction and any applicable affiliation/funding or hosting
policy must be established for the execution environment; nationality alone
does not establish them. No institutional affiliation or funding arrangement is
created or assumed by this decision. No access to identifying keys is part of this plan;
any outside ability to identify participants would require reassessing the scope.

The following project choices can be fixed now, without external contact:

| Condition | Selected implementation boundary |
| --- | --- |
| Purpose and linkage | Research-method reconstruction only; no clinical decisions, participant contact, reidentification or linkage beyond the pinned study annotations and membership. |
| Retention | Inputs, join keys, folds, scores and fitted models remain in process memory. No persistent dataset or private output directory is needed for this run. Do not claim an institution-approved location where none has been established. |
| Runtime checks | On the **MacBook study-data host**, complete [macOS runtime preflight](#macos-runtime-preflight-study-data-host) before loading study bytes. On any host, disable data caches, R workspace saves, core dumps and data-bearing logs; inspect temporary-file/swap behavior. Do not claim certified erasure or provider retention controls without evidence. Applicable privacy rules still apply to transient processing. |
| Publication | Persist only reviewed aggregates, implementation, citations, hashes and execution metadata. No row-level outputs, patient-key hashes, models or source archives in Git, logs, chat or external AI services. |
| Attribution | Cite Chowdhury et al., the article version/supplements, the exact author member and any used package releases. For PDC-derived outputs, also provide the CC BY 4.0 link, indicate changes and include the CPTAC credit below. |
| Scientific review | External review **deferred** (Gate 0 Q4, 2026-11-05). Label any result **not externally reviewed**. Internal software checks do not replace it; recruitment remains deferred under the outreach hold. |
| Project code licensing | An owner license decision is still absent. Do not invent a grant to downstream users; this does not prevent writing or checking the project's own implementation. |

#### macOS runtime preflight (study-data host)

Apply on the owner's MacBook **before** live acquisition or fitting on study values.
Record pass/fail in the execution attestation context; automated cloud CI does
not substitute for this checklist.

**Docker Desktop (pinned combined runtime).**

- Run containers `--rm` with `--log-driver none`, a **read-only** root filesystem,
  `tmpfs` for `/tmp` and other writable temp dirs, `--ulimit core=0`, and **no**
  bind mounts or volumes for data.
- Set Docker Desktop **VM swap to 0** so tmpfs pages cannot spill to the VM disk
  image.

**Host.**

- Confirm `ulimit -c` is `0` and inspect `sysctl kern.coredump`.
- Inspect `sysctl vm.swapusage` and `fdesetup status` (FileVault implies
  encrypted swap when active).

**Acquisition and paths.**

- **Never** download study files through a browser; fetch inside the container
  (adapter acquisition path).
- Keep data off any **iCloud**, **Dropbox-synced** or **Time Machine**-backed
  project path.

**R.**

- Invoke R with `--no-save --no-restore`; disable persistent history for the run.

**Telemetry and cleanup.**

- Analytics sharing is optional; ensure **DiagnosticReports** cannot retain run
  data relevant to this project.
- After the run, verify no leftover containers or volumes hold study data.

**Architecture (CONJECTURE).** If the pinned image is **amd64** and runs under
emulation on Apple Silicon, numerical results may differ from the recorded
pinned-image runs. Record the machine architecture in the execution context; treat
an **arm64** image rebuild or a **cross-architecture synthetic equivalence
check** as a precondition before comparing study-data AUROC to the synthetic
baseline — not established here.

The no-retention choice resolves the need to select a persistent data location
for this particular run. It changes the future execution-record design:
patient-level provenance exists only during computation, while public records
retain sufficient protocol, input and environment hashes for deterministic
rerunning. It does not erase applicable privacy obligations or turn the selected
host into approved infrastructure by assertion.

PDC/CPTAC requests this credit; this project will include it when those data
are used: “Data used in this publication
were generated by the National Cancer Institute Clinical Proteomic Tumor Analysis
Consortium (CPTAC).” The official [PDC policy index](https://pdc-docs.cancer.gov/pdc-docs/assets/searchindex.json)
also requests PDC and primary-publication citations. Its encouragement of freely
available conclusions and discouragement of direct dataset IP claims are not
recast here as additional license prohibitions.

## Bounded search and retained evidence

The 2026-10-25 follow-up searched the exact member filename and full member hash
for an explicitly licensed duplicate. No usable candidate was located. A
DataCite title search returned TCIA DOI [10.7937/6rda-p940](https://doi.org/10.7937/6rda-p940)
and Panorama DOI [10.6069/vbsn-6k93](https://doi.org/10.6069/vbsn-6k93); neither
established the selected member's rights. ProTrack's current landing page and
app bundle contained no license/terms marker or selected-archive reference.
These are bounded negative checks, not proof that no terms or copy exist anywhere.
No research datasets were downloaded in this follow-up.

| Public source checked | Bytes | SHA-256 |
| --- | ---: | --- |
| [Article XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.xml) | 449,678 | `1d88848c7b3dcda6f6b7734922f2f75b0ddeb0796d682d900d68cc2ffddd187b` |
| [NLM article-version metadata](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.json) | 2,395 | `804de66c4ca5e78af3b73530445b192132c53fff416a5ed6ee87d25bf6703bec` |
| [PDC policy index](https://pdc-docs.cancer.gov/pdc-docs/assets/searchindex.json) | 1,970,657 | `b2434f7da44d3cef5a32b237504ddfecda0b1a9cf17d4dea7bb0e7b6cba30910` |
| [ProTrack landing](https://ptrc.cptac-data-view.org/) | 970 | `02c14fe966a02bdc6bda7678835271626dbafdb45af773f77beb8b7a30300e6e` |
| [ProTrack app bundle](https://ptrc.cptac-data-view.org/js/app.6e170241.js) | 394,682 | `cf2dd3532d3c0be574a180afb2ac9fd9ebe7a1ad24ac28bb19014feee1ba072a` |
| [TCIA collection](https://www.cancerimagingarchive.net/collection/ptrc-hgsoc/) | 293,277 | `8bcc49e20fe4599cba3a571add1817ca8f97cef3a3b8c2a74b9360ca80e8dd4f` |
| [OHRP guidance](https://www.hhs.gov/ohrp/coded-private-information-or-biospecimens-used-research.html) | 188,021 | `f952cf0493e5aea992e9493a8b2e8727be2c0bc0dc19d495fd523c5266ea51ae` |
| [Canadian Copyright Act s.29](https://laws-lois.justice.gc.ca/eng/acts/C-42/section-29.html) | 34,676 | `b448c1fd5df615f9ed071138a4ffd8b32762cb67f3b2444851cbcea4d633b6f1` |
| [CCH judgment, WIPO full PDF](https://www.wipo.int/wipolex/en/text/600136) | 355,812 | `3e586ac725a3ca37dcabbf4921353ef5ca87613d669b47be556627a984ea2f64` |
| [TCPS introduction](https://ethics.gc.ca/eng/tcps2-eptc2_2022_introduction.html) | 16,707 | `269ad653492f45ee434ee00e9935c7af8d397329038219ec54094f4afef4208d` |
| [TCPS scope interpretations](https://ethics.gc.ca/eng/policy-politique_interpretations_scope-portee.html) | 53,818 | `31e8b10ad8bc38396345e3ba9015d6740a954af58b98003f328e6db1b4b2d0b7` |
| [TCPS chapter 2](https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter2-chapitre2.html) | 57,180 | `6c422bd1326484f6f7e8ce7e2e64c3bf2ba98598bba0711f2d513d6fddd0d92b` |
| [TCPS chapter 5](https://ethics.gc.ca/eng/tcps2-eptc2_2022_chapter5-chapitre5.html) | 54,931 | `1ccc414b2af7c61179a2a644b0362b75a508d076c3db6972f538ac09ab847059` |
| [OPC commercial-activity guidance](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/r_o_p/02_05_d_19/) | 23,635 | `73aa3bded6a64c403c6dad91feda0b163bdbef9afd14de68daa8727c9742da19` |

The NLM record identifies PMC10414761 version 1 and lists MMC1/MMC4 media with
their existing MD5 pins. This associates them with the article-version license
metadata; it is not a newly discovered independent workbook license.

The remaining execution conditions before study-data fitting: (a) dated owner
attestation (Gate 0 Q2); (b) macOS preflight on the MacBook; (c) no row-level
leakage; (d) A2 option B and A3 implementation per amendment 1. The owner
recorded Gate 0 sign-off on 2026-11-05 (Q2): before live acquisition of study
files, a real-source input check or any fitting on study values, the owner must
maintain a dated attestation of the actual execution context and give a new
explicit instruction to run. An automated session's own checks never satisfy
this condition.
The subsequent
[synthetic validation](pilot-001-synthetic-validation.md) implements and tests the
fixed reconstruction choices with original code and public software packages.
It resolves the software-build step, including dependency/license inspection,
without ingesting study values or closing these execution-context conditions.

The [source-adapter follow-up](pilot-001-source-adapter.md) implements pinned-byte
acquisition and parsing and tests them with artificial files and mocked requests.
Its probe verified 40 combined-runtime controls on 2026-10-25 for the earlier image,
including disabled Docker logs (the 2026-10-27 rebuild still needs its own probe),
while keeping processing location, actual host terms and applicable
obligations explicitly unverified. Those conditions must cover acquisition and
Python parsing as well as R execution; no study-data run is opened by these checks.
