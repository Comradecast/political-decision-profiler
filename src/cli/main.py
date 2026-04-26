import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from src.core.engine import ProfilerEngine
from src.schema.profile_schema import Profile
from src.schema.question_schema import Question


def load_questions(path: str | Path) -> List[Question]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Questions file must contain a JSON list.")

    return [Question.model_validate(item) for item in data]


def load_answers(path: str | Path) -> Dict[str, str]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Answers file must contain a JSON object.")

    return {str(question_id): str(option_id) for question_id, option_id in data.items()}


def collect_answers_from_file(questions: List[Question], answers: Dict[str, str]) -> List[tuple[Question, str]]:
    question_ids = {question.id for question in questions}
    answer_ids = set(answers.keys())
    missing = question_ids - answer_ids
    extra = answer_ids - question_ids
    if missing or extra:
        raise ValueError(f"Answer mismatch. Missing: {missing}, Extra: {extra}")

    responses = []
    for question in questions:
        selected_option_id = answers[question.id]
        if selected_option_id not in {option.id for option in question.options}:
            raise ValueError(f"Invalid option {selected_option_id} for question {question.id}")

        responses.append((question, selected_option_id))

    return responses


def collect_answers_interactive(questions: List[Question]) -> List[tuple[Question, str]]:
    responses = []
    for question in questions:
        print()
        print(f"{question.id}: {question.scenario}")
        for option in question.options:
            print(f"  {option.id}: {option.label}")

        valid_option_ids = {option.id for option in question.options}
        while True:
            selected_option_id = input("Select option id: ").strip()
            if selected_option_id in valid_option_ids:
                responses.append((question, selected_option_id))
                break
            print("Invalid option id. Please try again.")

    return responses


def format_profile(profile: Profile) -> str:
    lines = [
        "=== PROFILE SUMMARY ===",
        "",
        "Values:",
        f"- Market Preference: {profile.values.market_preference:.1f}",
        f"- Decision Authority: {profile.values.decision_authority:.1f}",
        f"- Fairness Preference: {profile.values.fairness_preference:.1f}",
        "",
        "Decision Behavior:",
        f"- Risk Tolerance: {profile.decision_behavior.risk_tolerance:.1f}",
        f"- Time Horizon: {profile.decision_behavior.time_horizon:.1f}",
        f"- Intervention Style: {profile.decision_behavior.intervention_style:.1f}",
        f"- System Trust: {profile.decision_behavior.system_trust.aggregate:.1f}",
        "",
        "Metadata:",
        f"- Confidence: {profile.metadata.confidence_score:.2f}",
        f"- Consistency: {profile.metadata.consistency_score:.2f}",
        "",
        "Insights:",
    ]

    if profile.insights:
        for insight in profile.insights:
            lines.append(f"- [{insight.title}] {insight.description}")
    else:
        lines.append("- None")

    lines.extend(["", "Contradictions:"])
    if profile.contradictions:
        for contradiction in sorted(profile.contradictions, key=lambda item: -item.severity):
            dimensions = " vs ".join(contradiction.related_dimensions)
            lines.append(f"- [{contradiction.severity:.2f}] {contradiction.description} ({dimensions})")
    else:
        lines.append("- None")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Political Decision Profiler.")
    parser.add_argument("--questions", required=True, help="Path to a JSON file containing questions.")
    parser.add_argument("--output-json", action="store_true", help="Print the full profile as JSON.")

    answer_mode = parser.add_mutually_exclusive_group(required=True)
    answer_mode.add_argument("--answers", help="Path to a JSON object mapping question_id to option_id.")
    answer_mode.add_argument("--interactive", action="store_true", help="Prompt for answers interactively.")

    return parser


def run(args: argparse.Namespace) -> Profile:
    questions = load_questions(args.questions)
    if args.answers:
        responses = collect_answers_from_file(questions, load_answers(args.answers))
    else:
        responses = collect_answers_interactive(questions)

    return ProfilerEngine().process_responses(responses)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        profile = run(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3

    if args.output_json:
        print(profile.model_dump_json(indent=2))
    else:
        print(format_profile(profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
