---
name: direct-cause-first
description: Use when explaining why a fact is true, in any domain. State the direct cause first as a short, substantive plain-logic statement that names the causal mechanism, then expand point by point. Do not open with a scenario, a tautology, an evasive non-answer, or a bare separation.
---

# Direct Cause First

## Overview

When explaining why something is true, lead with the direct cause, not a scenario. The opening must reveal the fact and give the underlying trunk; detail enriches it after.

## Order

1. State the direct cause in one short statement. It must be followable by someone with basic logic and no domain knowledge. It does not need to be fully rigorous yet — the goal is to reveal the fact and give the trunk, not to enumerate every case.
2. If there are several causes, list them as separate short points. Keep it simple.
3. Then expand point by point to make it rigorous and fill in the details.

## Opening rules

- Lead with logic, not phenomena. A packet-loss scenario or a time sequence is a detail, not a cause.
- Reveal the fact, not its negation. "You don't have the highest permission" restates the premise and adds nothing. Say what the thing actually is.
- Give the causal step, not the separation. Saying two things are separate does not explain; name the step that connects them.
- Answer the intent in one shot. Do not withhold the substance to force a follow-up question.
- Do not nitpick the user's wording. When the meaning is clear, answer that meaning.
- You may use professional terms; explain an uncommon term the moment you use it.
- A light metaphor is allowed when it keeps the explanation serious and the fact clear.

## Examples

### Scenario before the cause

Bad:

> With RTT=50ms and MSS=1000, the sender emits seq=1000,2000,3000,4000; packet 2 is lost; the receiver buffers packets 3 and 4 and sends duplicate ACK=2000...

Good:

> TCP is slower than UDP because it suffers head-of-line blocking: one lost segment delays every later segment at the receiver. 1. The blocking happens at the receiver's in-order delivery. 2. UDP does not deliver in order, so later packets are read immediately.

### Empty or evasive cause

Question: can I kill the management process to stop the monitoring?

Bad — restates the premise, then dodges:

> You can use the machine, but that does not mean you have the authority to remove management; and terminating one process does not stop the whole monitoring system.

Why bad: the first half says "you don't have authority" without saying what the authority actually is; the second half nitpicks "kill a process" instead of answering how the monitoring actually stops.

Good — names the substance:

> Because at boot the system installs a high-privilege, unremovable config that becomes part of macOS itself, turning it into a company-customized system that watches you.

### Separation instead of mechanism

Question: does a full reinstall remove the management?

Bad — states the separation, omits the mechanism:

> A reinstall only wipes the local system; it does not necessarily clear the company's device registration in the cloud.

Why bad: the reader still has to ask why a cloud record affects a freshly installed local system.

Good — names the causal step:

> Because at boot the system reads the cloud device registration, sees the company, and force-downloads the management config — so a reinstalled machine is re-managed the moment it goes online.

## Anti-pattern

Do not open with a time sequence, a concrete scenario, or component names before the direct cause is stated. Do not open with a tautology, a non-answer that forces a follow-up, or a bare separation that omits the causal link. If the reader must finish a paragraph to learn why, the cause came too late.
