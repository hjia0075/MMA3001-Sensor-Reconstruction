import numpy as np
from case_comparison import comparison_tables


def test_hidden_values_never_affect_predictions_and_known_nodes_unchanged():
    t = np.arange(16)*600.
    y = 20 + np.arange(16)*.1
    context, points, metrics = comparison_tables(t, y, 4, 10)
    changed = y.copy(); changed[4:10] += 100
    other, _, _ = comparison_tables(t, changed, 4, 10)
    assert points.input_after_mask.isna().all()
    for method in ['forward_fill', 'linear', 'cubic', 'pchip']:
        col = f'{method}_prediction'
        np.testing.assert_allclose(context[col], other[col])
        np.testing.assert_allclose(context.loc[~context.is_hidden, col],
                                   context.loc[~context.is_hidden, 'original_value'])
        np.testing.assert_allclose(points[f'{method}_signed_error'],
                                   points[col]-points.original_value)
    assert len(points) == 6 and len(metrics) == 4
