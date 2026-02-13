from pipeline.fit import estimate_horizon


def test_estimate_horizon_returns_curve() -> None:
    points = [
        {"human_minutes": 4, "score_binarized": 1},
        {"human_minutes": 8, "score_binarized": 1},
        {"human_minutes": 16, "score_binarized": 0},
        {"human_minutes": 32, "score_binarized": 0},
    ]
    horizon, beta, curve = estimate_horizon(points)
    assert horizon > 0
    assert isinstance(beta, float)
    assert len(curve) >= 2


def test_estimate_horizon_handles_noisy_late_rebound() -> None:
    points = [
        {"human_minutes": 4, "score_binarized": 0},
        {"human_minutes": 8, "score_binarized": 1},
        {"human_minutes": 16, "score_binarized": 0},
        {"human_minutes": 32, "score_binarized": 1},
    ]
    horizon, _, curve = estimate_horizon(points)

    # First bin is already below 50%; late rebounds should not inflate horizon.
    assert horizon == 4.0
    assert all("success_smoothed" in p for p in curve)
