from pipeline.transform import infer_domain, normalize_run


def test_infer_domain_explicit_map() -> None:
    assert infer_domain("pico_ctf pico_ctf/104") == "cybersecurity"
    assert infer_domain("mlab mlab/w1d1") == "ml_research"
    assert infer_domain("code_completion code_completion/foo") == "software_engineering"
    assert infer_domain("data_cleaning_arjun data_cleaning_arjun/x") == "data_analysis"
    assert infer_domain("arithmetic arithmetic/1") == "reasoning"


def test_infer_domain_fallback() -> None:
    assert infer_domain("totally_new_task totally_new_task/1") == "unknown"


def test_normalize_run_maps_required_fields() -> None:
    run = {
        "alias": "model-a",
        "task_family": "code_completion",
        "task_id": "code_completion/t-1",
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
