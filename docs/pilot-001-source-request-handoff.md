# Source request handoff

Status: sent (2026-11-04, 10:07 UTC); awaiting answers from the authors.
The owner sent the request from their own GitHub account. Automated sessions
never send or record a send without the owner's explicit instruction and evidence.

## Text and destination

The [source request](../templates/pilot-001-source-request.md) contains the five
questions and the sending history. Its introduction and all five items needed
the owner's review as one message. The earlier authorization of the code-audit
questions did not approve every part of the consolidated text.

The code-audit addendum is now on main through merged
[#7](https://github.com/Foundation-0/project-asma/pull/7). The request still
asks for missing source information.

The sent text is a condensed adaptation of
`templates/pilot-001-source-request.md`: the same five topics, with
lower-priority items grouped under “If convenient”. The authoritative sent text
is the public issue body; it is not duplicated in this repository.

## Sending record

| Field | Record |
| --- | --- |
| Date sent | 2026-11-04, 10:07 UTC |
| Channel | GitHub issue on `WangLab-MSSM/CPTAC_Ovarian_Chemo_Response` (standalone issue, not a comment on upstream issue #1) |
| Public link, or `sent by email` | [Issue #4 — Reproducing Figure 3D: questions on inputs, label coding and environment](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/issues/4) |
| Sender | Owner (Alkindus Arifuddin), from GitHub account `ahrazzle` |
| Status | Sent; awaiting answers |
| Commit containing the sent text | Not applicable — sent text is the public issue (see link) |
| Differences from that committed text | Condensed adaptation of the template: same five topics; lower-priority items under “If convenient”. See the issue for the exact wording. |

Keep recipient addresses and private correspondence outside this repository.
This table is the canonical sending record.
[Issue #8](https://github.com/Foundation-0/project-asma/issues/8) and the request
header should point to it (for example, “sent; see handoff record”) rather than
duplicating the date and link. Automated sessions never infer or record a send;
the table, the header and issue #8 change only on the owner's explicit
instruction, with the owner's evidence.

## Recording an answer

For each answer, record the question number, a source link or a private-source
description, the aggregate clarification, and which assumption it changes.
Update the code-audit addendum, protocol and reconstruction contract together
when the answer affects them. Preserve superseded assumptions as dated history.

No answer establishes execution permission by itself. Research runs still need
the owner attestations and execution checks in the
[roadmap](roadmap.md). Patient-level files, scores, labels and linkage rows do
not belong in the request, replies, issue, or repository.

## Review before handoff

- The full text reflects the current repository and asks neutral questions.
- Unresolved source provenance and the score discrepancy retain their limits.
- The owner confirmed the final text and chose to send on 2026-11-04.
- The sending record above reflects the owner's evidence.
- Before sending, the addendum link in the message still matched main: if
  `docs/pilot-001-code-audit-addendum.md` changed after the pinned commit,
  repin the link to a main commit that contains the current version and note
  that commit under "Differences from that committed text".
