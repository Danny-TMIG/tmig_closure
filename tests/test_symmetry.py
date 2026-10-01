"""Symmetry reduction tests."""

from tmig_closure import canonical, count_vector, orbit_key, stabilizer_size


def test_canonical_is_sorted():
    assert canonical(["c", "a", "b", "a"]) == ("a", "a", "b", "c")


def test_canonical_idempotent():
    items = ["z", "x", "y"]
    assert canonical(canonical(items)) == canonical(items)


def test_count_vector_depends_on_alphabet_order():
    assert count_vector(["a", "a", "c"], alphabet=["a", "b", "c"]) == (2, 0, 1)


def test_count_vector_invariant_under_permutation():
    assert count_vector(["a", "b", "a"], ["a", "b"]) == count_vector(["b", "a", "a"], ["a", "b"])


def test_orbit_key_groups_by_multiset():
    assert orbit_key(["a", "a", "b"]) == orbit_key(["b", "a", "a"])


def test_orbit_key_sorted():
    assert orbit_key(["c", "a", "b", "a"]) == (("a", 2), ("b", 1), ("c", 1))


def test_stabilizer_size_trivial_for_distinct():
    assert stabilizer_size(["a", "b", "c"]) == 1


def test_stabilizer_size_uses_factorials():
    assert stabilizer_size(["a", "a", "b", "b"]) == 4
    assert stabilizer_size(["a", "a", "a"]) == 6


def test_stabilizer_empty_is_one():
    assert stabilizer_size([]) == 1
