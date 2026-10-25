"""Verification of common context masks and isolation of hidden references."""
import numpy as np
from sensitivity_analysis import paired_candidates, context_predictions, CONTEXTS
from reconstruction import METHODS


def test_common_masks_support_all_contexts_and_continuous_core():
    t=np.arange(100)*600.
    candidates=paired_candidates(t,3600)
    assert candidates
    for i,j in candidates:
        assert i>=8 and j+8<=len(t) and j-i==6
        assert np.max(np.diff(t[i-1:j+1]))<=900


def test_all_context_predictions_ignore_hidden_values():
    t=np.arange(40)*600.;y=20+.03*np.arange(40)
    changed=y.copy();changed[12:18]+=100
    for context in CONTEXTS:
        for method in METHODS:
            np.testing.assert_allclose(context_predictions(t,y,12,18,context,method),
                                       context_predictions(t,changed,12,18,context,method))


def test_core_gaps_are_not_used_as_reference_truth():
    t=np.r_[np.arange(20)*600.,20000+np.arange(20)*600.]
    for i,j in paired_candidates(t,3600):
        assert np.max(np.diff(t[i-1:j+1]))<=900
