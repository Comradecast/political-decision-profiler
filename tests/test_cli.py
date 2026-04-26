import json

from src.cli.main import load_questions, main


def test_loads_sample_questions_json():
    questions = load_questions("examples/sample_questions.json")

    assert len(questions) == 2
    assert questions[0].id == "q1"
    assert questions[0].options[0].id == "o1"


def test_runs_non_interactive_answers(tmp_path, capsys):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o1", "q2": "o1"}), encoding="utf-8")

    exit_code = main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
    ])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "=== PROFILE SUMMARY ===" in output
    assert "Values:" in output
    assert "Decision Behavior:" in output
    assert "Metadata:" in output
    assert "Insights:" in output
    assert "Contradictions:" in output


def test_format_profile_contains_expected_sections(tmp_path):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o1", "q2": "o1"}), encoding="utf-8")

    main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
    ])

    questions = load_questions("examples/sample_questions.json")
    assert questions


def test_no_crash_on_valid_input(tmp_path):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o2", "q2": "o2"}), encoding="utf-8")

    assert main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
    ]) == 0


def test_answers_mode_rejects_missing_question_ids(tmp_path, capsys):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o1"}), encoding="utf-8")

    exit_code = main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
    ])

    error = capsys.readouterr().err
    assert exit_code == 2
    assert "Answer mismatch" in error
    assert "q2" in error


def test_answers_mode_rejects_extra_question_ids(tmp_path, capsys):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o1", "q2": "o1", "q999": "o1"}), encoding="utf-8")

    exit_code = main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
    ])

    error = capsys.readouterr().err
    assert exit_code == 2
    assert "Answer mismatch" in error
    assert "q999" in error


def test_output_json_prints_profile_json(tmp_path, capsys):
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"q1": "o1", "q2": "o1"}), encoding="utf-8")

    exit_code = main([
        "--questions",
        "examples/sample_questions.json",
        "--answers",
        str(answers_path),
        "--output-json",
    ])

    output = capsys.readouterr().out
    payload = json.loads(output)
    assert exit_code == 0
    assert "values" in payload
    assert "decision_behavior" in payload
    assert "metadata" in payload
    assert "insights" in payload
    assert "contradictions" in payload


def test_missing_questions_file_returns_validation_exit_code(capsys):
    exit_code = main([
        "--questions",
        "examples/does-not-exist.json",
        "--answers",
        "examples/answers.json",
    ])

    error = capsys.readouterr().err
    assert exit_code == 2
    assert "Error:" in error
