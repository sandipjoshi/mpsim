"""Unit tests for inital MPS states."""

import pytest

import numpy as np
import tensornetwork as tn

from mps.mps import (MPS,
                     igate, xgate, zgate, hgate, cnot, swap,
                     zero_state, one_state, plus_state)


def test_mps_one_qubit():
    """Ensures an error is raised if the number of qubits is less than two."""
    with pytest.raises(ValueError):
        MPS(nqubits=1)


def test_is_valid_for_product_states():
    """Tests that a product state on different numbers of qubits is a valid MPS."""
    for n in range(2, 20):
        mps = MPS(nqubits=n)
        assert mps.is_valid()


def test_get_wavefunction_simple():
    """Tests getting the wavefunction of a simple MPS."""
    mps = MPS(nqubits=3)
    assert isinstance(mps.wavefunction, np.ndarray)
    assert mps.wavefunction.shape == (8,)
    correct = np.array([1.] + [0.] * 7, dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)


def test_get_wavefunction_deosnt_modify_mps():
    """Tests that getting the wavefunction of an MPS doesn't affect the actual MPS."""
    mps = MPS(nqubits=2)
    nodes = mps.get_nodes(copy=False)
    _ = mps.wavefunction
    a, b = nodes
    assert len(a.edges) == 2
    assert len(a.get_all_nondangling()) == 1
    assert len(a.get_all_dangling()) == 1
    assert len(b.edges) == 2
    assert len(b.get_all_nondangling()) == 1
    assert len(b.get_all_dangling()) == 1


def test_correctness_of_initial_product_state_two_qubits():
    """Tests that the contracted MPS is indeed the all zero state for two qubits."""
    mps = MPS(nqubits=2)
    lq, _ = mps.get_nodes()
    wavefunction_node = tn.contract(lq[1])
    wavefunction = np.reshape(wavefunction_node.tensor, newshape=(4,))
    correct = np.array([1, 0, 0, 0], dtype=np.complex64)
    assert np.array_equal(wavefunction, correct)


def test_correctness_of_initial_product_state():
    """Tests that the contracted MPS is indeed the all zero state for multiple qubits."""
    for n in range(3, 10):
        mps = MPS(n)
        wavefunction = mps.wavefunction
        correct = np.array([1] + [0] * (2**n - 1), dtype=np.complex64)
        assert np.array_equal(wavefunction, correct)


@pytest.mark.parametrize(["gate", "expected"],
                         [(xgate(), one_state),
                          (hgate(), plus_state),
                          (zgate(), zero_state),
                          (igate(), zero_state)])
def test_apply_oneq_gate_xgate(gate, expected):
    """Tests application of a single qubit gate to several MPS."""
    for n in range(2, 8):
        for j in range(n):
            mps = MPS(n)
            mps.apply_one_qubit_gate(gate, j)
            final_state = np.reshape(mps.get_node(j).tensor, newshape=(2,))
            assert np.array_equal(final_state, expected)


def test_apply_oneq_gate_to_all():
    """Tests correctness for final wavefunction after applying a NOT gate to all qubits in a two-qubit MPS."""
    mps = MPS(nqubits=2)
    mps.apply_one_qubit_gate_to_all(xgate())
    correct = np.array([0., 0., 0., 1.], dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)


def test_apply_oneq_gate_to_all_hadamard():
    """Tests correctness for final wavefunction after applying a Hadamard gate to all qubits in a five-qubit MPS."""
    n = 5
    mps = MPS(nqubits=n)
    mps.apply_one_qubit_gate_to_all(hgate())
    correct = 1 / 2**(n / 2) * np.ones(2**n)
    assert np.allclose(mps.wavefunction, correct)


def test_apply_twoq_cnot_two_qubits():
    """Tests for correctness of final wavefunction after applying a CNOT to a two-qubit MPS."""
    # In the following tests, the first qubit is always the control qubit.
    # Check that CNOT|10> = |11>
    mps = MPS(nqubits=2)
    mps.x(0)
    mps.apply_two_qubit_gate(cnot(), 0, 1)
    correct = np.array([0., 0., 0., 1.], dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)

    # Check that CNOT|00> = |00>
    mps = MPS(nqubits=2)
    mps.apply_two_qubit_gate(cnot(), 0, 1)
    correct = np.array([1., 0., 0., 0.], dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)

    # Check that CNOT|01> = |01>
    mps = MPS(nqubits=2)
    mps.x(1)
    mps.apply_two_qubit_gate(cnot(), 0, 1)
    correct = np.array([0., 1., 0., 0.], dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)

    # Check that CNOT|11> = |10>
    mps = MPS(nqubits=2)
    mps.x(-1)  # Applies to all qubits in the MPS
    mps.apply_two_qubit_gate(cnot(), 0, 1)
    correct = np.array([0., 0., 1., 0.], dtype=np.complex64)
    assert np.array_equal(mps.wavefunction, correct)


# def test_apply_twoq_cnot_two_qubits_flipped_control_and_target():
#     """Tests for correctness of final wavefunction after applying a CNOT to a two-qubit MPS."""
#     # In the following tests, the first qubit is always the target qubit.
#     # Check that CNOT|10> = |10>
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 1., 0.], dtype=np.complex64)
#     assert np.allclose(wavefunction, correct)
#
#     # Check that CNOT|00> = |00>
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1., 0., 0., 0.], dtype=np.complex64)
#     assert np.allclose(wavefunction, correct)
#
#     # Check that CNOT|01> = |11>
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate(mps.xgate(), 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 1.], dtype=np.complex64)
#     assert np.allclose(wavefunction, correct)
#
#     # Check that CNOT|11> = |01>
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate_to_all(mps.xgate(), mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 1., 0., 0.], dtype=np.complex64)
#     assert np.allclose(wavefunction, correct)
#
#
# def test_apply_twoq_identical_indices_raises_error():
#     """Tests that a two-qubit gate application with identical indices raises an error."""
#     mps2q = mps.get_zero_state_mps(nqubits=2)
#     mps3q = mps.get_zero_state_mps(nqubits=3)
#     mps9q = mps.get_zero_state_mps(nqubits=9)
#     with pytest.raises(ValueError):
#         for mpslist in (mps2q, mps3q, mps9q):
#             mps.apply_two_qubit_gate(mps.cnot(), 0, 0, mpslist)
#
#
# def test_apply_twoq_non_adjacent_indices_raises_error():
#     """Tests that a two-qubit gate application with non-adjacent indices raises an error."""
#     n = 10
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     for (a, b) in [(0, 2), (0, 9), (4, 6), (2, 7)]:
#         with pytest.raises(ValueError):
#             mps.apply_two_qubit_gate(mps.cnot(), a, b, mpslist)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_gate_indexB_great_than_indexA_raise_error(left):
#     """Tests that applying a two-qubit gate with indexA > indexB raises an error.
#
#     TODO: This is really due to my inability to find the bug for this case. We can get around this by,
#      e.g. for a CNOT, conjugating by Hadamard gates to flip control/target.
#     """
#     mpslist = mps.get_zero_state_mps(nqubits=10)
#     with pytest.raises(ValueError):
#         mps.apply_two_qubit_gate(mps.cnot(), 6, 5, mpslist, keep_left_canonical=left)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_cnot_four_qubits_interior_qubits(left):
#     """Tests with a CNOT on four qubits acting on "interior" qubits."""
#     mpslist = mps.get_zero_state_mps(nqubits=4)             # State: |0000>
#     mps.apply_one_qubit_gate(mps.xgate(), 1, mpslist)       # State: |0100>
#     mps.apply_two_qubit_gate(mps.cnot(),
#                              1,
#                              2,
#                              mpslist,
#                              keep_left_canonical=left)      # State: Should be |0110>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=4)             # State: |0000>
#     mps.apply_two_qubit_gate(mps.cnot(),
#                              1,
#                              2,
#                              mpslist,
#                              keep_left_canonical=left)     # State: Should be |0000>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_cnot_four_qubits_edge_qubits(left):
#     """Tests with a CNOT on four qubits acting on "edge" qubits."""
#     mpslist = mps.get_zero_state_mps(nqubits=4)             # State: |0000>
#     mps.apply_one_qubit_gate(mps.xgate(), 2, mpslist)       # State: |0010>
#     mps.apply_two_qubit_gate(mps.cnot(),
#                              2,
#                              3,
#                              mpslist,
#                              keep_left_canonical=left)      # State: Should be |0011>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=4)             # State: |0000>
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)       # State: |1000>
#     mps.apply_two_qubit_gate(mps.cnot(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)      # State: Should be |1100>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_cnot_five_qubits_all_combinations(left):
#     """Tests applying a CNOT to a five qubit MPS with all combinations of indices.
#
#     That is, CNOT_01, CNOT_02, CNOT_03, ..., CNOT_24, CNOT_34 where the first number is
#     the control qubit and the second is the target qubit.
#     """
#     n = 5
#     indices = [(a, a + 1) for a in range(n - 1)]
#
#     for (a, b) in indices:
#         # Apply the gates
#         mpslist = mps.get_zero_state_mps(nqubits=n)
#         mps.apply_one_qubit_gate(mps.xgate(), a, mpslist)
#         mps.apply_two_qubit_gate(mps.cnot(), a, b, mpslist, keep_left_canonical=left)
#         wavefunction = mps.get_wavefunction_of_mps(mpslist)
#         # Get the correct wavefunction
#         correct = np.zeros((2**n,))
#         bits = ["0"] * n
#         bits[a] = "1"
#         bits[b] = "1"
#         correct[int("".join(bits), 2)] = 1.
#         assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_swap_two_qubits(left):
#     """Tests swapping two qubits in a two-qubit MPS."""
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)           # State: |10>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 1., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |00>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate(mps.xgate(), 1, mpslist)           # State: |01>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |10>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 1., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate_to_all(mps.xgate(), mpslist)       # State: |11>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |11>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 1.])
#     assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_twoq_swap_two_qubits(left):
#     """Tests swapping two qubits in a two-qubit MPS."""
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)           # State: |10>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 1., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1., 0., 0., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate(mps.xgate(), 1, mpslist)           # State: |01>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 1., 0.])
#     assert np.array_equal(wavefunction, correct)
#
#     mpslist = mps.get_zero_state_mps(nqubits=2)                 # State: |00>
#     mps.apply_one_qubit_gate_to_all(mps.xgate(), mpslist)       # State: |11>
#     mps.apply_two_qubit_gate(mps.swap(),
#                              0,
#                              1,
#                              mpslist,
#                              keep_left_canonical=left)          # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 0., 0., 1.])
#     assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_apply_swap_five_qubits(left):
#     """Tests applying a swap gate to an MPS with five qubits."""
#     n = 5
#     for i in range(n - 1):
#         mpslist = mps.get_zero_state_mps(nqubits=n)
#         mps.apply_one_qubit_gate(mps.xgate(), i, mpslist)
#         mps.apply_two_qubit_gate(mps.swap(), i, i + 1, mpslist, keep_left_canonical=left)
#         wavefunction = mps.get_wavefunction_of_mps(mpslist)
#         # Get the correct wavefunction
#         correct = np.zeros((2 ** n,))
#         bits = ["0"] * n
#         bits[i + 1] = "1"
#         correct[int("".join(bits), 2)] = 1.
#         assert np.array_equal(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_qubit_hopping_left_to_right(left):
#     """Tests "hopping" a qubit with a sequence of swap gates."""
#     n = 8
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     for i in range(1, n - 1):
#         mps.apply_two_qubit_gate(mps.swap(), i, i + 1, mpslist, keep_left_canonical=left)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.zeros(2**n)
#     correct[0] = correct[2**(n - 1)] = 1. / np.sqrt(2)
#     assert np.allclose(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_bell_state(left):
#     """Tests for wavefunction correctness after preparing a Bell state."""
#     n = 2
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = 1. / np.sqrt(2) * np.array([1., 0., 0., 1.])
#     assert np.allclose(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_twoq_gates_in_succession(left):
#     """Tests for wavefunction correctness after applying a series of two-qubit gates."""
#     n = 2
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)                                   # State: |10>
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)                               # State: |10>
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)       # State: |11>
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)                                   # State: |01>
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([0., 1., 0., 0.])
#     assert np.allclose(wavefunction, correct)
#
#
# def test_left_vs_right_canonical_two_qubit_one_gate():
#     """Performs a two-qubit gate keeping left-canonical and right-canonical,
#     checks for equality in final wavefunction.
#     """
#     n = 2
#     lmps = mps.get_zero_state_mps(nqubits=n)
#     rmps = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.xgate(), 0, lmps)
#     mps.apply_one_qubit_gate(mps.xgate(), 0, rmps)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, lmps, keep_left_canonical=True)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, rmps, keep_left_canonical=False)
#     lwavefunction = mps.get_wavefunction_of_mps(lmps)
#     rwavefunction = mps.get_wavefunction_of_mps(rmps)
#     cwavefunction = np.array([0., 0., 0., 1.])
#     assert np.array_equal(lwavefunction, cwavefunction)
#     assert np.array_equal(rwavefunction, cwavefunction)
#
#
# def test_apply_cnot_right_to_left_sweep_twoq_mps():
#     """Tests applying a CNOT in a "right to left sweep" in a two-qubit MPS."""
#     n = 2
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.xgate(), 1, mpslist)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=False)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=False)
#     mps.apply_one_qubit_gate_to_all(mps.hgate(), mpslist)
#
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=False)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=False)
#     assert mps.is_valid(mpslist)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_valid_mps_indexA_greater_than_indexB_twoq_three_qubits(left):
#     """Tests successive application of two CNOTs in a three-qubit MPS."""
#     n = 3
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#     assert mps.is_valid(mpslist)
#
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     mps.apply_one_qubit_gate(mps.hgate(), 1, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     mps.apply_one_qubit_gate(mps.hgate(), 1, mpslist)
#     assert mps.is_valid(mpslist)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_three_cnots_is_swap(left):
#     for n in range(2, 11):
#         mpslist = mps.get_zero_state_mps(nqubits=n)
#         mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)
#
#         # CNOT(0, 1)
#         mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#
#         # CNOT(1, 0)
#         mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#         mps.apply_one_qubit_gate(mps.hgate(), 1, mpslist)
#         mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#         mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#         mps.apply_one_qubit_gate(mps.hgate(), 1, mpslist)
#
#         # CNOT(0, 1)
#         mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=left)
#
#         wavefunction = mps.get_wavefunction_of_mps(mpslist)
#         correct = np.zeros((2**n))
#         correct[2**(n - 2)] = 1
#         assert np.allclose(wavefunction, correct)
#
#
# def test_apply_cnot_right_to_left_sweep_threeq_mps():
#     """Tests applying a CNOT in a "right to left sweep" in a three-qubit MPS retains a valid MPS."""
#     n = 3
#     mpslist = mps.get_zero_state_mps(nqubits=n)
#     mps.apply_one_qubit_gate(mps.xgate(), 2, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 1, 2, mpslist, keep_left_canonical=True)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, keep_left_canonical=False)
#     assert mps.is_valid(mpslist)
#
#
# def test_qubit_hopping_left_to_right_and_back():
#     """Tests "hopping" a qubit with a sequence of swap gates in several n-qubit MPS states."""
#     for n in range(2, 20):
#         mpslist = mps.get_zero_state_mps(nqubits=n)
#         mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)
#         for i in range(n - 1):
#             mps.apply_two_qubit_gate(mps.swap(), i, i + 1, mpslist, keep_left_canonical=True)
#         for i in range(n - 1, 0, -1):
#             mps.apply_two_qubit_gate(mps.swap(), i - 1, i, mpslist, keep_left_canonical=False)
#         assert mps.is_valid(mpslist)
#         wavefunction = mps.get_wavefunction_of_mps(mpslist)
#         correct = np.zeros(2**n)
#         correct[2**(n - 1)] = 1
#         assert np.allclose(wavefunction, correct)
#
#
# @pytest.mark.parametrize(["left"],
#                          [[True], [False]])
# def test_cnot_truncation_two_qubits_product(left):
#     """Tests applying a CNOT with truncation on a product state."""
#     for maxsvals in range(1, 5):
#         mpslist = mps.get_zero_state_mps(nqubits=2)
#         mps.apply_one_qubit_gate(mps.xgate(), 0, mpslist)
#         mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, max_singular_values=maxsvals, keep_left_canonical=left)
#         wavefunction = mps.get_wavefunction_of_mps(mpslist)
#         correct = np.array([0., 0., 0., 1.])
#         assert np.array_equal(wavefunction, correct)
#
#
# def test_cnot_truncation_on_bell_state():
#     """Tests CNOT with truncation on the state |00> + |10>."""
#     # Test with truncation
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, max_singular_values=1)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1 / np.sqrt(2), 0., 0., 0.])
#     assert np.allclose(wavefunction, correct)
#
#     # Test keeping all singular values ==> Bell state
#     mpslist = mps.get_zero_state_mps(nqubits=2)
#     mps.apply_one_qubit_gate(mps.hgate(), 0, mpslist)
#     mps.apply_two_qubit_gate(mps.cnot(), 0, 1, mpslist, max_singular_values=2)
#     wavefunction = mps.get_wavefunction_of_mps(mpslist)
#     correct = np.array([1 / np.sqrt(2), 0., 0., 1 / np.sqrt(2)])
#     assert np.allclose(wavefunction, correct)
