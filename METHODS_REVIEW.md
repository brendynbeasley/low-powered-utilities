# Methods review: Laffont and Tirole (1991)

- **Paper.** Jean-Jacques Laffont and Jean Tirole, "The Politics of Government Decision-Making: A Theory of
  Regulatory Capture," *Quarterly Journal of Economics* 106(4), November 1991, pp. 1089–1127.
- **Statistical focus.** Proposition 1 (producer protection leads to a lower-powered incentive scheme for the
  inefficient type and a lower rent for the efficient type), and Proposition 2 (an organized non-industry group
  can raise the firm's rent when both prefer an uninformed principal).
- **Review standard.** Internal consistency of the formal results, explicitness of the assumptions, and the
  testability of the predictions with observable data.
- **What was read.** The full text of the October 1988 working paper (MIT Department of Economics Working Paper
  No. 506, from MIT's DSpace), Sections 1 through 5, including Propositions 1 to 3 and the remarks around them, and
  the abstract of the published 1991 article as listed on RePEc/IDEAS. The published article itself was not read,
  so equation and proposition numbers below refer to the working paper and may differ in the journal version.

## Methods summary

The paper is a formal theory with no data. It extends the regulation model of Laffont and Tirole (1986) to a
three-tier hierarchy. A firm produces output $`q`$ at cost $`C = (\beta - e)q`$, where $`\beta`$ takes one of two
values and $`e`$ is unobserved effort with convex disutility $`\psi(e)`$. Congress, which maximizes total surplus
with a shadow cost of public funds $`\lambda`$, observes cost, output and the report of an agency. With probability
$`p`$ the agency receives hard evidence of $`\beta`$, which it can reveal or conceal. Interest groups can pay the
agency to conceal it, at a cost of $`1 + \lambda_f`$ (firm) or $`1 + \lambda_e`$ (environmentalists) per dollar the
agency receives. The authors show (Appendix 1 of the working paper) that Congress can restrict attention to
collusion-proof schemes, so no bribes are paid in equilibrium. The results come from comparing the
collusion-proof optimum with the collusion-free benchmark.

## Research design

A comparative-statics analysis of an optimal-contracting problem. The design is internally standard for the
field: the benchmark (Section 3) reproduces the known asymmetric-information result, and each extension adds one
coalition incentive constraint.

## Sampling strategy

Does not apply. There is no sample.

## Sample size

Does not apply.

## Inclusion and exclusion criteria

Does not apply. The analogue is the model's scope conditions. Production is essential (the firm cannot be shut
down) in Sections 3 to 5; Section 6 relaxes this. All parties are risk neutral, the agency is indispensable, the
agency's probability of learning the truth is exogenous, interest groups observe the agency's signal, and contracts
are signed after information arrives.

## Independent and dependent variables

In model terms, the exogenous parameters are $`\lambda`$, $`\lambda_f`$, $`\lambda_e`$, $`p`$, $`\nu`$ (the
probability of the efficient type) and $`\Delta\beta`$. The endogenous outcomes are the inefficient type's effort
(the power of its incentive scheme), output and price, the firm's rent $`\Phi(e)`$, and the agency's reward for
reporting.

## Statistical methods

Does not apply in the empirical sense. The method is constrained optimization with first-order conditions,
assuming concavity of the welfare function (stated as an assumption, with sufficient conditions in footnotes) and
$`\psi''' \geq 0`$ so that optimal schemes are nonstochastic.

## Reported effect sizes

No numerical effect sizes are reported. The results are signs of derivatives. The paper mentions one empirical
magnitude in passing, a shadow cost of public funds "of the order of .3 for the U.S." attributed to econometric
studies, used to argue that public collection of funds is cheaper than private collection.

## Confidence intervals

Does not apply.

## P-values, if applicable

Does not apply.

## Missing data treatment

Does not apply.

## Stated limitations

The authors state that treating Congress as a benevolent maximizer is an oversimplification and give three
justifications. They note that the agency's investigative effort is taken as exogenous, that the analysis is
heuristic in the text with full proofs in appendices, and that constraints on the regulator's choice set cannot be
explained in a model where the principal is benevolent, which they defer to a companion paper.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Rent of the efficient type | $`\Phi(e) = \psi(e) - \psi(e - \Delta\beta)`$, dollars | Eq. (3.8)–(3.9), working paper | Information rent as a function of the effort asked of the inefficient type; increasing and convex | The size of rents in any real industry |
| Collusion-free effort condition | $`\psi'(e) = q - \frac{\lambda}{1+\lambda}\frac{\nu}{1-\nu}\Phi'(e)`$ | Eq. (3.11) | Downward distortion of the inefficient type's effort under asymmetric information alone | Any effect of capture; this is the benchmark |
| Coalition incentive constraint | $`(1+\lambda_f)(s_1 - s^*) \geq \Phi(e)`$ | Eq. (4.1)–(4.3) | Agency reward needed to outbid the firm's bribe | That such transfers occur; in equilibrium they do not |
| Proposition 1(b) | Sign: inefficient type's effort lower than without collusion | Section 4 | Producer protection lowers the power of incentives | How large the reduction is, or that observed low power is caused by capture rather than by information alone |
| Proposition 1(e) | Sign: efficient type's rent lower than without collusion | Section 4 | Capture threat reduces the firm's rent | That captured industries have low profits, since realized capture is outside the model |
| Proposition 1(f) | Sign: effort, rent and output increase with $`\lambda_f`$ | Section 4 | Cheaper influence means lower power | Which real institutions have low $`\lambda_f`$ |
| Proposition 2(c) | Sign: a fall in $`\lambda_e`$ raises the firm's rent | Section 5 | Interest groups that both want an uninformed principal reinforce each other | Generality beyond essential production, which Section 6 qualifies |
| Proposition 3 | Consumers of the good have no political power | Section 5 | Consumers gain only from full information, so cannot profit from bribing for concealment | Behavior when consumers also act as information providers (noted in footnote 22) |
| Shadow cost of public funds | about 0.3 | Section 5, bracketed remark | Order of magnitude used for a plausibility argument | A calibration; no source is given in the text read |

## Interpretation notes

- The headline prediction is about the contract, not about bribes. Because the optimal scheme is collusion-proof,
  the model predicts no observed corruption, only weaker incentives and smaller rents. Tests that look for capture
  in profits test a different theory.
- Proposition 1 distorts only the inefficient type's scheme in the asymmetric-information state. Observed average
  power across firms mixes types and states, so the theory's prediction for an average is a direction, not a level.
- Low power is predicted both by asymmetric information alone (Section 3) and, more strongly, by the threat of
  capture (Section 4). Evidence of low-powered regulation is consistent with the paper but does not by itself
  discriminate between the two mechanisms. Only variation in $`\lambda_f`$ or $`p`$ does.
- The model leaves open which real institutions correspond to a low $`\lambda_f`$. Direct election of regulators
  could make campaign spending a cheap channel of influence, but it may also raise the visibility of regulation, as
  later argued by Besley and Coate (2003).

## Unanswered questions

- How large are the distortions for plausible parameters? The paper gives no calibration.
- How does the result change when the agency's probability of discovery is chosen by Congress through the agency's
  budget, rather than fixed?
- What is the observable counterpart of $`\lambda_f`$? The paper discusses ethics laws, intervenor funding and
  post-employment rules qualitatively but does not map them to the parameter.
- Do the results survive repeated interaction, where the agency and firm deal with each other over many rate cases?

## Items requiring expert verification

- Whether equation and proposition numbering in the 1991 journal version matches the 1988 working paper read here.
- Every entry in the statistics extraction table, including the proposition parts cited (1(b), 1(e), 1(f), 2(c))
  and the shadow-cost remark of about 0.3, was taken from the working paper and has not been checked against the
  published article.
- Which forms of side transfer (money, future employment, personal relationships, campaign support) the published
  article names as channels of collusion.
- Whether the published version retains the risk-aversion remark and the multiple-interest-group results in the
  same form.
- Whether the linear-contract implementation used in this repository, $`b = \psi'(e)/q`$, carries over exactly to
  the two-type model of the paper. It is exact for a firm facing a linear scheme with fixed output, and Laffont and
  Tirole's 1993 book discusses implementation of the optimal menu by linear contracts, but this review did not
  check the book.

How the modern rerun relates: this repository does not reproduce anything in the paper, which has no data. It
takes the sign prediction of Proposition 1 and asks whether American electric regulation is low-powered and
whether it is lower-powered where commissioners are elected, a proxy for a cheaper channel of influence that is
itself contestable.
