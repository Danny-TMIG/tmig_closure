# Theory

<!-- SPDX-License-Identifier: MIT -->

## 1. The lattice

Let `A` be a finite alphabet of capability primitives. The power set `2^A` ordered by
inclusion is a complete lattice. A configuration is an element `X of 2^A`; a rule is a
pair `(P, C)` with `P, C subset A` finite.

## 2. Immediate-consequence operator

Define `T_R : 2^A -> 2^A`:

    T_R(X) = X union { C | (P, C) in R, P subset X }

T_R is monotone (`X subset Y => T_R(X) subset T_R(Y)`) and extensive (`X subset T_R(X)`).

## 3. Closure operator

By Knaster-Tarski, a monotone function on a complete lattice has a least fixed point
above any starting element. Define

    cl_R(X) = union_{n>=0} T_R^n(X)

The Kleene chain stabilises in at most `|A \ X|` steps. cl_R is a Tarski closure operator:

- Extensive: `X subset cl_R(X)`
- Monotone: `X subset Y => cl_R(X) subset cl_R(Y)`
- Idempotent: `cl_R(cl_R(X)) = cl_R(X)`

## 4. Symmetry

The symmetric group S_A acts by renaming primitives. cl is equivariant. The orbit
invariant is the count-vector over the sorted alphabet. |Stab(X)| = product of
factorials of multiplicities.

## 5. What is not claimed

- Rules are inputs, not learned.
- Capabilities are not scored.
- Primitives are opaque symbols. Interpretation lives above the kernel.


## 7. The verification triad

Every closure problem admits three orthogonal questions:

1. **Conformance** -- does the artifact match its declaration?
   `close(declared) == close(actual)`.
2. **Coherence** -- do two artifacts agree under primitive renaming?
   `orbit_key(a) == orbit_key(b)`, or equivalently the count-vector
   over a shared alphabet.
3. **Coordination** -- do many agents agree on a fixpoint?
   The per-agent verdicts are folded by quorum, consensus, or one
   of the other lattice reductions.

Each answer is a state in Belnap's FOUR lattice. The triad is the
product of three states; its verdict is the lattice meet under the
truth order. Because FOUR is a distributive bilattice, triad
composition is commutative, associative, and idempotent -- so partial
verifications can be combined without loss of soundness.
