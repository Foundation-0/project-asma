# Source request handoff

Status: unsent. The owner reviews and sends the request from their own account.
This record prepares that handoff and does not authorize an automated send.

## Text and destination

The [source request](../templates/pilot-001-source-request.md) contains the five
questions and the intended destination. Its introduction and all five items need
the owner's review as one message. The earlier authorization of the code-audit
questions did not approve every part of the consolidated text.

The code-audit addendum is now on main through merged
[#7](https://github.com/Foundation-0/project-asma/pull/7). The request still
asks for missing source information.

## Sending record

The owner fills these fields only after sending:

| Field | Record |
| --- | --- |
| Date sent | Not sent |
| Channel | Not selected |
| Public link, or `sent by email` | Not available |
| Commit containing the sent text | Not selected |
| Differences from that committed text | Not applicable |

Keep recipient addresses and private correspondence outside this repository.
This table is the canonical sending record. Once it is filled,
[issue #8](https://github.com/Foundation-0/project-asma/issues/8) and the request
header should point to it (for example, "sent; see handoff record")
rather than duplicating the date and link. Automated sessions never infer or
record a send; the table, the header and issue #8 change only on the owner's
explicit instruction, with the owner's evidence. Keep issue #8 open until this
table records the send.

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
- The owner confirms the final text and chooses whether and when to send.
- The sending record remains empty until the owner provides evidence.
- Before sending, the addendum link in the message still matches main: if
  `docs/pilot-001-code-audit-addendum.md` changed after the pinned commit,
  repin the link to a main commit that contains the current version and note
  that commit under "Differences from that committed text".
