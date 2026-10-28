# The maximum-pair bound holds for arbitrary three anchors

Date: 2026-10-26.

Let H be a finite k-uniform family with (7,2). For ANY three
edges A1,A2,A3, permitting repetitions, put

    X=max_{i<j}|Ai intersect Aj|.

Then

    tau(H) <= X+ceil(k/2).                            (1)

No empty-common-intersection hypothesis or asymptotic error is
needed. This strengthens `good_triple_maximum_bound.md` and
removes the union-size term in `max_intersection_triple_bound.md`.
It does not prove that an appropriate triple with X<=k/4+o(k)
exists in every family, so it does not settle Problem 644(i).

## Notation and the small union case

Let C be the common intersection, of size e. Outside C, let the
exclusive pair regions have sizes p>=q>=r. Put P=p+q+r,
t=ceil(k/2), and T=e+p+t=X+t. The union of all pair intersections
has size e+P. The earlier integral anchor lemma gives

    tau(H)<=max(e+P,T).                               (2)

Its construction is recalled below to make the argument independent
of a numerical certificate. Thus (1) already follows if e+P<=T.
For the remaining case assume e+P>T and tau(H)>T. Equivalently,
q+r>t. Also q<=k/2<=t, since p>=q and e+p+q<=k.

Relabel the three anchors so that their regions are

    A1=C union Pq union Pp union S1,
    A2=C union Pq union Pr union S2,
    A3=C union Pp union Pr union S3,

where |Pp|=p, |Pq|=q, |Pr|=r and all seven named regions are
disjoint. Thus the singleton sizes are k-e-p-q, k-e-q-r,
and k-e-p-r, respectively.

## One integer query and three blocks

Query all of C,Pp,Pq and exactly t-q points of Pr. This fits
because 0<=t-q<r, and its total size is e+p+t=T. An edge E
avoids the query. Let

    H0=E intersect Pr, |H0|=h<=q+r-t,
    A=E intersect S1, |A|=a<=k-e-p-q,
    B=E intersect S2, |B|=b<=k-e-q-r,
    D=E intersect S3, |D|=d<=k-e-p-r,
    W=E minus (A1 union A2 union A3).

Start three blocks with the following sets:

    B1=C union H0 union Pq union D,
    B2=C union H0 union Pp union B,
    B3=C union Pr union A.

Their sizes L1,L2,L3 satisfy

    L1=e+h+q+d <= k+2q-p-t <= p+t <= T,
    L2=e+h+p+b <= k+p-t <= p+t <= T,
    L3=e+r+a   <= k+r-p-q < k+p-t <= T.

For the strict inequality in the last line, use
2p+q-r>=q+r>t. The other inequalities use q<=p and 2t>=k.

The as yet unassigned required points are S1 minus A and W.
They are disjoint, and their combined size is

    F=(k-e-p-q-a)+(k-h-a-b-d).

The total load after assigning all of them once is

    L1+L2+L3+F = 2k+2e+h+r-a
      <= 2k+2e+q+2r-t
      <= 2k+2e+3p-t
      <= 3e+3p+3t = 3T.

The last step uses 4t>=2k and e>=0. Each residual capacity
T-Li is a nonnegative integer and their sum is at least F.
Distribute the F points among them in any order. This is an
integer allocation; there is no LP or rounding loss.

Every two-point transversal of A1,A2,A3,E lies wholly in at
least one completed block. To check this exhaustively by type:

* A point of C must be paired with a point of E. C lies in all
  blocks and every point of E lies in their union.
* Without a point of C, a cover of the original triple uses two
  different pair regions, or Pr with S1, Pp with S2, or Pq with S3.
* The first kind must use H0, since E avoids Pp and Pq. H0 lies
  in all three blocks and every point of the pair regions lies
  in some block.
* For Pr with S1, either the Pr point lies in H0, or the S1
  point lies in A. H0 is in all blocks, all S1 points were
  assigned, and Pr union A lies in B3.
* The other two kinds must use B or D, and are covered by B2
  or B1 respectively.

Choose an edge of H avoiding each completed block, which is
possible since tau(H)>T. Together with the four selected anchors
these are at most seven edges, with no two-transversal. This
contradicts (7,2), proving (1) in the remaining case.

## Recall of the integral anchor lemma used in (2)

Set T0=max(e+P,e+p+t), and s=T0-e. Query C and all three pair
regions. An avoiding edge E has traces a_i in the opposite
singletons and w outside the anchors, with sum a_i+w=k. After
putting C in all three blocks, cover the three bicliques (p_i,a_i)
within capacities s and include every E point in the block union.

Any two component loads sum to at most 2p+k<=2s. Thus at most
one component overflows. If none does, put them in separate
blocks; 3s>=P+k leaves room for the w outside points.

If (u,v) overflows, call the other component loads B,F. Let
U=2s-u-v-B and V=2s-u-v-F. Both are nonnegative. The singleton
cap v<=k-e-P+u and u<=p give

    2u+v+P+k <= 3u+2k-e <= 3p+2k-e <= 4s.

Consequently U+V>=u. Split the u-side into integers
u2=max(0,u-V), u3=u-u2, with membership masks {1,2},{1,3}.
Put s-u points of the v-side in block 1 only and the remaining
u+v-s points in both blocks 2,3. Put the B,F components in
blocks 2,3. All biclique edges are covered and all loads are
at most s. The total load before the w outside points is
2u+v+P+sum a_i-s; the displayed inequality leaves total
residual capacity at least w. Place those points there.

All points of E are included. Adding C to each block therefore
covers C times E as well. Three avoiding edges contradict (7,2)
just as before. This proves (2) with exact integer blocks.

## Consequence under a high transversal hypothesis

If tau(H)>ck+1, every triple has a pair intersection exceeding
(c-1/2)k. Therefore the graph on the edges of H, in which a
pair is adjacent when its intersection is at most (c-1/2)k,
is triangle-free. This applies even to triples with a positive
common core. Existing bounds that only imposed this condition
on good triples can now impose it on all triples.
