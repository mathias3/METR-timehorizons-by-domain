from pipeline.transform import infer_domain, normalize_run


def test_infer_domain_keywords() -> None:
    assert infer_domain("ctf reverse engineering") == "cybersecurity"
    assert infer_domain("ml training data science") == "ml_engineering"
    assert infer_domain("software implementation devops") == "software_engineering"
    assert infer_domain("math reasoning qa") == "reasoning"


def test_normalize_run_maps_required_fields() -> None:
    run = {
        "alias": "model-a",
        "task_family": "SWE implementation",
        "task_id": "t-1",
        "score_binarized": 1,
        "score_cont": 0.83,
        "human_minutes": 42,
    }
    out = normalize_run(run, "metr_hcast", "src_1", {"model-a": "2025-06-01"})
    assert out["benchmark"] == "metr_hcast"
    assert out["domain"] == "software_engineering"
    assert out["model"] == "model-a"
    assert out["release_date"] == "2025-06-01"
    assert out["score_binarized"] == 1
    assert out["human_minutes"] == 42.0
