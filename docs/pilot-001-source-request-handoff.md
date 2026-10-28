# Source request handoff

Status: unsent. The owner reviews and sends the request from their own account.
This record prepares that handoff and does not authorize an automated send.

## Text and destination

The [source request](../templates/pilot-001-source-request.md) contains the five
questions and the intended destination. Its introduction and all five items need
the owner's review as one message. The earlier authorization of the code-audit
questions did not approve every part of the consolidated text.

The code-audit addendum is now on main through merged PR 7. The request still
asks for missing source information. The synthetic and adapter runs on main
used generated inputs and did not reproduce the study's clinical result.

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
Record the sending date and public link, if any, in issue 8 and in the request
header. This draft must not close that issue before sending is recorded.

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

Prepared by gpt-forge using gpt-6.1-sol for Ahraz Arifuddin.
