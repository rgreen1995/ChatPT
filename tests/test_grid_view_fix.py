from unittest.mock import MagicMock, patch

from chat_pt.progress_page import render, render_log_workout


def test_render_css_content():
    """Verify that the render function injects the expected compact/orientation-agnostic CSS."""
    with patch("streamlit.session_state") as mock_state:
        mock_state.user_id = 1
        with patch("chat_pt.progress_page.get_user_consultations", return_value=[]):
            with patch("streamlit.markdown") as mock_markdown:
                render()

                # Find the <style> block
                style_arg = None
                for call in mock_markdown.call_args_list:
                    arg = call[0][0]
                    if "<style>" in arg:
                        style_arg = arg
                        break

                assert (
                    style_arg is not None
                ), "render() should call st.markdown with a <style> block"

                # Compact, workout-scoped rules should be present
                assert ".chatpt-log-row" in style_arg
                assert ":has(.chatpt-log-row)" in style_arg
                assert ".exercise-header-compact" in style_arg
                assert ".compact-header" in style_arg
                assert ".set-circle" in style_arg

                # Scoped to horizontal blocks containing the row marker (not a vertical block).
                assert (
                    '[data-testid="stHorizontalBlock"]:has(.chatpt-log-row) .stNumberInput'
                    in style_arg
                )

                # Mobile override keeps rows horizontal at small widths.
                assert "@media (max-width: 640px)" in style_arg


def test_render_log_workout_column_ratios():
    """Verify that the render_log_workout function uses the compact column ratios."""
    workout_plan = {
        "schedule": {
            "Day 1": {
                "focus": "Full Body",
                "exercises": [{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
            }
        }
    }

    with patch("streamlit.session_state") as mock_state:
        mock_state.user_id = 1
        mock_state.exercise_logs = {}
        mock_state.get.return_value = False

        with patch("streamlit.selectbox", return_value="Day 1"):
            with patch("streamlit.columns") as mock_columns:

                def columns_side_effect(ratios):
                    return tuple(MagicMock() for _ in ratios)

                mock_columns.side_effect = columns_side_effect

                with patch("streamlit.components.v1.html"):
                    with patch(
                        "chat_pt.utils.group_exercises_by_sequence",
                        return_value={
                            "solo_0": [(0, workout_plan["schedule"]["Day 1"]["exercises"][0])]
                        },
                    ):
                        with patch(
                            "chat_pt.utils.get_sorted_sequence_keys", return_value=["solo_0"]
                        ):
                            render_log_workout(1, workout_plan)

                    ratios_found = [call[0][0] for call in mock_columns.call_args_list]
                    # Compact redesign uses [0.35, 1.0, 1.0, 0.8] (rebalanced
                    # so inputs pack tightly on mobile without huge gaps).
                    assert [0.35, 1.0, 1.0, 0.8] in ratios_found
                    # Both header row and each set row use those ratios, so >=2 (1 header + 3 sets)
                    count = sum(1 for r in ratios_found if r == [0.35, 1.0, 1.0, 0.8])
                    assert count >= 2


def test_render_log_workout_saves_entered_weight_and_reps():
    """Verify entered number inputs are persisted and saved."""

    class FakeSessionState(dict):
        def __getattr__(self, item):
            if item in self:
                return self[item]
            raise AttributeError(item)

        def __setattr__(self, key, value):
            self[key] = value

    workout_plan = {
        "schedule": {
            "Day 1": {
                "focus": "Full Body",
                "exercises": [{"name": "Squat", "sets": 1, "reps": 10, "rest_seconds": 60}],
            }
        }
    }

    fake_state = FakeSessionState(user_id=1)

    def columns_side_effect(ratios):
        return tuple(MagicMock() for _ in ratios)

    def button_side_effect(*_args, **kwargs):
        return kwargs.get("key") == "save_workout"

    expander_mock = MagicMock()
    expander_mock.__enter__.return_value = expander_mock
    expander_mock.__exit__.return_value = False

    with patch("streamlit.session_state", fake_state):
        with patch("streamlit.selectbox", return_value="Day 1"):
            with patch("streamlit.columns", side_effect=columns_side_effect):
                with patch("streamlit.number_input", side_effect=[42.5, 12]):
                    with patch("streamlit.button", side_effect=button_side_effect):
                        with patch("streamlit.expander", return_value=expander_mock):
                            with patch("streamlit.text_area", return_value=""):
                                with patch("streamlit.markdown"):
                                    with patch("streamlit.caption"):
                                        with patch("streamlit.success"):
                                            with patch("streamlit.balloons"):
                                                with patch("streamlit.rerun"):
                                                    with patch("time.sleep"):
                                                        with patch(
                                                            "chat_pt.progress_page.save_exercise_progress"
                                                        ) as mock_save:
                                                            with patch(
                                                                "chat_pt.utils.group_exercises_by_sequence",
                                                                return_value={
                                                                    "solo_0": [
                                                                        (
                                                                            0,
                                                                            workout_plan[
                                                                                "schedule"
                                                                            ]["Day 1"]["exercises"][
                                                                                0
                                                                            ],
                                                                        )
                                                                    ]
                                                                },
                                                            ):
                                                                with patch(
                                                                    "chat_pt.utils.get_sorted_sequence_keys",
                                                                    return_value=["solo_0"],
                                                                ):
                                                                    render_log_workout(
                                                                        1, workout_plan
                                                                    )

    mock_save.assert_called_once()
    saved_kwargs = mock_save.call_args.kwargs
    assert saved_kwargs["weight"] == 42.5
    assert saved_kwargs["reps"] == 12


def test_render_log_workout_renders_sets_for_every_superset_exercise():
    """
    Regression test: each exercise inside a superset group must render its own
    set rows (weight + reps number inputs), not just the last exercise in the group.
    """

    class FakeSessionState(dict):
        def __getattr__(self, item):
            if item in self:
                return self[item]
            raise AttributeError(item)

        def __setattr__(self, key, value):
            self[key] = value

    # Superset group "2": two exercises (2A and 2B), 2 sets each.
    ex_a = {
        "name": "Bench Press",
        "sets": 2,
        "reps": 8,
        "rest_seconds": 60,
        "sequence": "2A",
    }
    ex_b = {
        "name": "Bent-Over Row",
        "sets": 2,
        "reps": 8,
        "rest_seconds": 60,
        "sequence": "2B",
    }
    workout_plan = {
        "schedule": {
            "Day 1": {
                "focus": "Upper Body",
                "exercises": [ex_a, ex_b],
            }
        }
    }

    fake_state = FakeSessionState(user_id=1)

    def columns_side_effect(ratios):
        return tuple(MagicMock() for _ in ratios)

    # Track every number_input key so we can assert weight/reps were rendered
    # for BOTH exercises in the superset (not just the last one).
    rendered_input_keys = []

    def number_input_side_effect(*_args, **kwargs):
        rendered_input_keys.append(kwargs.get("key", ""))
        # default value returned
        return 0

    expander_mock = MagicMock()
    expander_mock.__enter__.return_value = expander_mock
    expander_mock.__exit__.return_value = False

    rendered_markdown = []

    def markdown_side_effect(*args, **_kwargs):
        if args:
            rendered_markdown.append(args[0])

    with patch("streamlit.session_state", fake_state):
        with patch("streamlit.selectbox", return_value="Day 1"):
            with patch("streamlit.columns", side_effect=columns_side_effect):
                with patch("streamlit.number_input", side_effect=number_input_side_effect):
                    with patch("streamlit.button", return_value=False):
                        with patch("streamlit.expander", return_value=expander_mock):
                            with patch("streamlit.text_area", return_value=""):
                                with patch("streamlit.markdown", side_effect=markdown_side_effect):
                                    with patch("streamlit.caption"):
                                        with patch("streamlit.components.v1.html"):
                                            with patch(
                                                "chat_pt.utils.group_exercises_by_sequence",
                                                return_value={2: [(0, ex_a), (1, ex_b)]},
                                            ):
                                                with patch(
                                                    "chat_pt.utils.get_sorted_sequence_keys",
                                                    return_value=[2],
                                                ):
                                                    render_log_workout(1, workout_plan)

    # Superset header must be rendered
    assert any("🔗 Superset" in m for m in rendered_markdown), "Superset header was not rendered"

    # Both exercise headers must be present in output
    joined = "\n".join(rendered_markdown)
    assert "Bench Press" in joined, "First superset exercise header missing"
    assert "Bent-Over Row" in joined, "Second superset exercise header missing"

    # Both exercises must render their own weight+reps inputs for every set.
    # Keys are of the form weight_<exercise_key>_<set_idx> and reps_<exercise_key>_<set_idx>.
    ex_a_weight_keys = [
        k for k in rendered_input_keys if k.startswith("weight_") and "Bench Press" in k
    ]
    ex_b_weight_keys = [
        k for k in rendered_input_keys if k.startswith("weight_") and "Bent-Over Row" in k
    ]
    ex_a_reps_keys = [
        k for k in rendered_input_keys if k.startswith("reps_") and "Bench Press" in k
    ]
    ex_b_reps_keys = [
        k for k in rendered_input_keys if k.startswith("reps_") and "Bent-Over Row" in k
    ]

    assert (
        len(ex_a_weight_keys) == 2
    ), f"Expected 2 weight inputs for first superset exercise, got {ex_a_weight_keys}"
    assert (
        len(ex_b_weight_keys) == 2
    ), f"Expected 2 weight inputs for second superset exercise, got {ex_b_weight_keys}"
    assert (
        len(ex_a_reps_keys) == 2
    ), f"Expected 2 reps inputs for first superset exercise, got {ex_a_reps_keys}"
    assert (
        len(ex_b_reps_keys) == 2
    ), f"Expected 2 reps inputs for second superset exercise, got {ex_b_reps_keys}"

    # Exercise-log entries must exist for BOTH exercises (not only the last one)
    assert any(
        "Bench Press" in k for k in fake_state["exercise_logs"].keys()
    ), "Exercise log for the first superset exercise is missing"
    assert any(
        "Bent-Over Row" in k for k in fake_state["exercise_logs"].keys()
    ), "Exercise log for the second superset exercise is missing"
