# A computer-assisted bound for property (7,2)

Research certificate: 2026-10-26. This exposition: 2026-10-29.

This document supplies the mathematical reduction used by the exact
certificate. It is an internally checked research argument for external
review, not a formally mechanized proof or a claim of literature priority.

## 1. Statement and conventions

Let $H$ be a finite family of sets of cardinality $k\geq1$. Write
$\tau(H)$ for the minimum number of points meeting every member of $H$.
Assume that every subfamily of at most seven members has transversal
number at most two. The claimed theorem is

$$\tau(H)\leq\frac{11}{13}k+8.\tag{1}$$

Repeated selections of an edge below cause no problem: the distinct
selected edges still form a subfamily of at most seven members.

Finite families suffice for the extremal function. More generally, if
a family of finite sets has no transversal of size $t$, some finite
subfamily witnesses this. Prove the claim by induction on $t$: choose
one edge $A$; for each $v\in A$, the subfamily avoiding $v$ has no
$(t-1)$-transversal and hence has a finite witness. Their union with
$A$ has no $t$-transversal. The case $t=0$ is immediate.

For the main argument put

$$c=\frac{11}{13},\qquad a_0=c-\frac12=\frac9{26}.$$

For $k\geq20$ suppose, towards a contradiction, that $\tau(H)>ck+8$.
Every set of at most $ck+8$ points can then be avoided by an edge.
All lower-case region sizes below are normalized by dividing by $k$.

## 2. A general covering principle

Fix $r$ anchor edges with empty common intersection. A *candidate pair*
is a pair of points meeting all anchors. Suppose there are $7-r$ blocks
such that each candidate pair has both its points in at least one block.
If each block has at most $T$ points, then $\tau(H)\leq T$.

Indeed, if $\tau(H)>T$, choose an edge avoiding each block. Any
two-transversal of the anchors and these new edges would be a candidate
pair, but it lies inside a block and misses its corresponding new edge.
This contradicts (7,2). A one-point transversal of the anchors is
impossible because their common intersection is empty.

A triple of anchors with empty common intersection will be called
*good*. For a good triple $A_1,A_2,A_3$, let $P_i$ be the pair region
opposite $A_i$ and $S_i$ the region belonging to $A_i$ only. If the
pair-region sizes are $fk,gk,jk$, the singleton sizes are

$$|S_1|=(1-g-j)k,\quad |S_2|=(1-f-j)k,\quad |S_3|=(1-f-g)k.$$

The candidate-pair graph joins each two different $P$-regions and
joins $P_i$ to $S_i$. There are no other candidate pairs. In particular,
a point outside all three anchors cannot belong to a candidate pair.

## 3. Two integer bounds for a good triple

### Maximum-pair bound

If $X$ is the largest of the three actual pair-intersection sizes, then

$$\tau(H)\leq X+\lceil k/2\rceil.\tag{2}$$

The complete integer construction, including its auxiliary anchor
lemma, is in [docs/maximum_pair_lemma.md](docs/maximum_pair_lemma.md).
It in fact proves (2) for arbitrary triples; only good triples are
needed here. Consequently, under our high-transversal assumption,
every good triple has a pair larger than $a_0k$.

### Short symmetric-difference bound

Put $P=|P_1|+|P_2|+|P_3|$. Split each of the six regions into two
halves, rounding to integers, and assign the halves to four blocks
using these membership masks (bits $1,2,4,8$ label the blocks):

| Region | Its two masks |
| --- | --- |
| $P_1$ | 3, 12 |
| $P_2$ | 5, 10 |
| $P_3$ | 9, 6 |
| $S_1$ | 5, 10 |
| $S_2$ | 3, 12 |
| $S_3$ | 3, 12 |

For every adjacent pair of regions, each allowed mask of one region
intersects every allowed mask of the other. Thus the blocks cover all
candidate pairs. Each mask pair partitions the four block labels, so
each block receives one half of every region and has size at most
$(3k-P)/2+3$. Section 2 gives

$$\tau(H)\leq\frac{3k-P}{2}+3.\tag{3}$$

Every good normalized profile $(a,b,d)$ therefore satisfies

$$a,b,d\geq0,\quad a+b,a+d,b+d\leq1,\quad
a+b+d<3-2c=\frac{17}{13}.\tag{4}$$

## 4. Attained small and large pair intersections

Call a pair intersection small when it is at most $a_0k$, and large
otherwise. Put $T=\lfloor ck\rfloor+3$. Since $k\geq20$,

$$ck+2<T\leq ck+3<k.$$

Query $T$ points of any edge. An avoiding edge meets it in fewer than
$(1-c)k\leq a_0k$ points, so a small pair exists. Let $xk$ be the
largest actual small intersection.

In a pair attaining $xk$, query subsets of sizes
$\lfloor(T+xk)/2\rfloor$ and $\lceil(T+xk)/2\rceil$, each containing
the whole intersection. They fit, and their union has size $T$.
An avoiding edge gives a good profile $(p,x,r)$, relabelled so $p\geq r$.
The largest new intersection satisfies

$$2pk\leq2k-T-xk+1,$$

and hence $2p+x<2-c$. By (2) this triple cannot be all small. Thus a
large pair exists; let $Yk$ be the smallest actual large intersection.
We have

$$0\leq x\leq a_0<Y\leq p,\qquad r\leq p,\qquad
2p+x<2-c=\frac{15}{13}.\tag{5}$$

Every actual pair intersection is at most $xk$ or at least $Yk$.
There is no assumed forbidden interval: $x,Y$ are attained extrema
of the hypothetical family itself.

### Two large pairs and one small pair

For any good triple whose two large pair sizes are $bk,dk$ and whose
small outer-pair size is $sk$, we need

$$3-b-d-3Y+2x-s>c.\tag{6}$$

Here is the integer query proving it. Write $B=bk$, $D=dk$, $S=sk$,
$X=xk$, and $Z=Yk$. The middle edge meets the two outer edges in
$B,D$ points. Select $k-Z+1$ points in the middle edge. In the two
outer petals select respectively

$$k-B-Z+X+1,\qquad k-D-Z+X+1$$

points, both selections containing the entire $S$-point outer
intersection. These selections fit: $B+D\leq k$, $B,D\geq Z$,
$S\leq X$, and the integer gap gives $X+1\leq Z$.
Their total union size is

$$k(3-b-d-3Y+2x-s)+3.$$

If (6) failed, an avoiding edge would exist. Its intersection with
the middle edge is at most $Z-1$, hence at most $X$. In each outer
edge it has at most $X$ points in the middle edge and at most
$Z-X-1$ in the petal, again at most $Z-1$ and therefore at most
$X$. Together with the outer anchors it forms a good all-small
triple, contradicting (2). This proves (6).

## 5. Lexicographic selection and a global pair restriction

Among the good triples choose one whose decreasingly sorted profile
$(u,v,w)$ is lexicographically least. Thus $u\geq v\geq w$ and
$u>a_0$. Every good sorted profile $(L,B,S)$ has

$$L\geq u;\quad L=u\Rightarrow B\geq v;\quad
L=u, B=v\Rightarrow S\geq w.\tag{7}$$

Put $U=uk$, $V=vk$. If $U>0$, in the selected pair with intersection
$V$ query $k-U+1$ points from each edge, including the intersection.
This fits because $U+V\leq k$. The union has size
$2k-2U-V+2$ and must be a transversal: an avoiding edge would give
a good triple with pair sizes $(V,A,B')$, where $A,B'\leq U-1$.
This lowers the largest entry if $V<U$, or the middle entry if $V=U$.
For $U=0$ the next inequality is immediate. Hence

$$2u+v<2-c.\tag{8}$$

Since $c\geq2/3$, this implies $u<(2-c)/2\leq c$. For any actual
pair intersection $tk$ with $t<u$, query
$\lfloor k(c+t)/2\rfloor+1$ points in each edge, including its
intersection. Both selections fit and their union has at most $ck+2$
points. An avoiding edge gives a good triple whose other two pair
sizes are strictly below $(2-c-t)k/2$. If $2u+t\geq2-c$, all three
would be below $uk$, a contradiction. Thus every actual pair obeys

$$t\geq u\quad\hbox{or}\quad 2u+t<2-c.\tag{9}$$

This includes the attained pairs $x,Y$ and all pairs in the response
triples introduced next.

## 6. Four avoiding-edge queries and strict capacities

Choose an ordering $(f,g,j)$ of the selected profile and a fixed
$0\leq\theta\leq1$. Define

$$\delta_0=\max(0,f+g+j-c),\quad
\delta=(1-\theta)\delta_0+\theta f,\quad
L=c-f-g-j+\delta,\quad D=1-f-g.$$

The ordinary query is available when $g+j\leq c$. In this case
$0\leq\delta\leq f$ and $0\leq L\leq1-g-j$. Query $P_2,P_3$
completely, $\lceil k(f-\delta)\rceil$ points of $P_1$, and
$\lceil kL\rceil$ points of $S_1$.

For a targeted query choose a level $\ell\in\{u,v\}$ and set
$t=\delta+D-\ell$. Impose the additional guards

$$0\leq t\leq D,\qquad t\leq L.\tag{10}$$

Replace the $S_1$ selection by $\lceil k(L-t)\rceil$ points and
also select $\lceil kt\rceil$ points of $S_3$. For an ordinary
query set $t=0$. Every selection fits its integer-sized region.
The unrounded total is $ck$ and there are at most four rounded
selections, so the total is at most $ck+4$.

There are four possibly nonempty residual regions: $P_1,S_1,S_2,S_3$.
Add one further point from each nonempty residual region. The enlarged
query has at most $ck+8$ points, so it has an avoiding response edge $E$.
Let its four normalized traces be $h,a,b,d$, respectively. They obey

$$\begin{aligned}
0&\leq h\leq\delta,\\
0&\leq a\leq1+f-c-\delta+t,\\
0&\leq b\leq1-f-j,\\
0&\leq d\leq1-f-g-t,\\
h+a+b+d&\leq1.
\end{aligned}\tag{11}$$

Each positive cap in (11) is strict. Indeed, before the extra point
the integer residual size $N$ is at most the cap times $k$. If
$N>0$, one further queried point reduces it by one; if $N=0$ the
trace is already strictly below any positive cap. A zero cap forces
zero trace. There is no fixed real slack or limiting argument.

For a targeted query the $h,d$ caps sum to $\ell$. Thus
$\ell>0$ implies $h+d<\ell$. The model explicitly guards this
strict implication by $\ell>0$.

The four queries are exactly:

| Name | $(f,g,j)$ | $\theta$ | Target |
| --- | --- | --- | --- |
| U0 | $(u,v,w)$ | $0$ | ordinary |
| UhD | $(u,v,w)$ | $1/2$ | $\ell=u$ |
| U1D | $(u,v,w)$ | $1$ | $\ell=u$ |
| V1D | $(v,u,w)$ | $1$ | $\ell=v$ |

Only available queries constrain their formal responses. Distinct
queries may use different actual edges. Since $E$ avoids $P_2,P_3$,
the replacement profiles $(j,a,h+b)$ and $(g,a,h+d)$ are good.
All conditions (4), (6), (7), and (9) apply to them.

## 7. The explicit candidate-pair covers

For three good anchors, index the six regions by masses

$$(f,g,j,1-g-j,1-f-j,1-f-g).$$

The graph edges are $01,02,12,03,14,25$.

For those three anchors and a response edge from Section 6, index
the eight relevant classes by masses

$$(h,g,j,a,1-g-j-a,b,d,f-h).$$

Their graph edges are $01,02,03,04,15,26,37$. For example, class
0 is $E\cap P_1$ and must be paired with a point of the whole
opposite anchor, including its unused singleton region. Points in
$E$ outside the original three anchors cannot complete a pair
covering the original triple. This accounts for all candidate pairs.

When $h=0$, the exact relevant graph simplifies to three disjoint
bicliques, with masses $(f,g,j,a,b,d)$ and edges $03,14,25$.
That simplification is used only on the branch $h=0$.

Each support assigns to a region a list of nonzero membership masks
on the available blocks. For adjacent regions, every allowed mask
from one list must intersect every allowed mask from the other.
The checker tests every such pair, so every permitted allocation
of points to the lists covers all candidate pairs.

The complete lists are in
[verifier/targeted_0849_supports.json](verifier/targeted_0849_supports.json).
The numerical indices are labels, not omitted definitions.

| Application | Support kind | Labels |
| --- | --- | --- |
| Selected good triple | static, four blocks | 439, 449 |
| U0 and its anchors | tree, three blocks | 2031, 2047 |
| U0 when $h=0$ | biclique, three blocks | 882 |
| UhD and its anchors | tree, three blocks | 448 |
| UhD right replacement triple | static, four blocks | 449 |
| U1D and its anchors | tree, three blocks | 2029 |
| V1D and its anchors | tree, three blocks | 1552 |

## 8. Exact dual costs and integer rounding

For a fixed support, let $m_i$ be its normalized region masses and
let $\mathcal S_i$ be the permitted masks for region $i$. The least
fractional maximum block load is, by finite linear programming duality,

$$\max_{\lambda_b\geq0, \sum_b\lambda_b=1}
\sum_i m_i\min_{M\in\mathcal S_i}\sum_{b\in M}\lambda_b.\tag{12}$$

The simplex is subdivided by all equalities between subset sums of
$\lambda$. On every resulting cell the expression is linear, so
its maximum occurs at a cell vertex. These vertices are obtained
by intersecting the simplex with coordinate boundaries and
hyperplanes having coefficients in $\{-1,0,1\}$ with both signs.
Enumerating all independent choices of $b-1$ such hyperplanes is
complete for $b$ blocks. The exact enumeration yields ten directions
for three blocks and 101 for four blocks. The checker reconstructs
them and the resulting rational affine costs; it does not trust
discovery-time numerical projections.

If every cost for a support is at most $c$, a fractional allocation
with maximum load at most $ck$ exists. For a four-block support the
checker verifies at most three extra mask choices in total. For
three blocks choose an extreme feasible allocation: with $n$ positive
classes it has at most $n+3$ positive variables, from the $n$ mass
equalities and three load inequalities. Hence there are at most
three extra positive pieces beyond one per class.

In each class round all but one positive piece down to integers and
assign the integer remainder to the last permitted mask. The excess
load on any block is less than the number of rounded pieces, hence
at most three. The resulting integer blocks therefore have size at
most $ck+3$. By Section 2 these are incompatible with our assumption
$\tau(H)>ck+8$. Thus, whenever the corresponding anchor/query
conditions hold, at least one affine support cost must be strictly
greater than $c$.

## 9. Exact refutation of the necessary conditions

The preceding constructions imply 27 groups of rational linear
conditions with Boolean connectives. They are regenerated by
[lexicographic_bound_model.py](verifier/lexicographic_bound_model.py)
from the fixed configuration and the audited supports.

The saved model is
[targeted_eleven_thirteenths_model.json](verifier/targeted_eleven_thirteenths_model.json).
The certificate is
[targeted_eleven_thirteenths_certificate.json](verifier/targeted_eleven_thirteenths_certificate.json).
The checker requires exact equality between the regenerated model,
the saved model, and the certificate premises.

Each of the 919 arithmetic clauses has positive rational weights
whose weighted inequalities cancel all variables and give either
a positive constant at most zero, or a strict zero-at-most-zero
contradiction. Strict and non-strict atoms are distinguished.
Each weight and cancellation is checked using exact fractions.

The remaining propositional refutation uses reverse unit propagation
(RUP): for each added clause, negate it and unit-propagate the
already verified clauses until a contradiction is reached. All 63
additions are checked, including the final empty clause. The verifier
needs neither an SMT/SAT solver nor a floating-point optimizer.

Therefore the necessary conditions have no solution. This contradicts
the hypothetical family for every $k\geq20$ and proves (1) in that range.
The certificate proves this implication only together with the written
combinatorial necessity and rounding arguments in Sections 2-8.

## 10. Small ranks and asymptotic interpretation

For $2\leq k<20$, the published theorem $f(k,6)=k$ gives
$\tau(H)\leq k\leq11k/13+8$. For $k=1$, three distinct singleton
edges would already violate the local hypothesis, so $\tau(H)\leq2$.
The checker verifies these numerical comparisons; it does not reprove
the published small-rank theorem. See [REFERENCES.md](REFERENCES.md).

For completeness, the standard lower bound is
$f(k,7)\geq\lceil3k/4\rceil$. Take all $k$-subsets of a set of size
$N=\lceil7k/4\rceil-1$. Its transversal number is $N-k+1$.
Among seven such edges, padded by repetitions if necessary, there
are $7k>4N$ incidences, so some point belongs to at least five of
the seven rows. The remaining at most two edges intersect because
$N<2k$; one further point meets them. The $k=1$ case is immediate.

Consequently the claimed upper bound leaves the asymptotic interval
$[3/4,11/13]$. It neither identifies a limit nor resolves the
conjectured $3/4$ coefficient.
