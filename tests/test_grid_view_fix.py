from unittest.mock import MagicMock, patch

from chat_pt.progress_page import render, render_log_workout


def test_render_css_content():
    """Verify that the render function injects the expected CSS styles."""
    with patch("streamlit.session_state") as mock_state:
        mock_state.user_id = 1
        with patch("chat_pt.progress_page.get_user_consultations", return_value=[]):
            with patch("streamlit.markdown") as mock_markdown:
                render()

                # Check if markdown was called with a style block
                called_with_style = False
                for call in mock_markdown.call_args_list:
                    arg = call[0][0]
                    if "<style>" in arg:
                        called_with_style = True
                        # Verify key parts of the new CSS
                        assert "/* ===== NUMBER INPUT — compact on ALL screen sizes ===== */" in arg
                        assert ".stNumberInput {" in arg
                        assert "max-width: 80px !important;" in arg
                        assert '.stNumberInput [data-testid="stNumberInputStepDown"]' in arg
                        assert '.stNumberInput [data-testid="stNumberInputStepUp"]' in arg
                        assert ".stNumberInput button {" not in arg
                        assert (
                            '.stNumberInput div[data-baseweb="input"] > div:last-child {' not in arg
                        )
                        assert "/* ===== MOBILE-SPECIFIC TIGHTENING (portrait) ===== */" in arg
                        assert "@media (max-width: 640px) {" in arg
                        assert "max-width: 60px !important;" in arg  # Mobile tighter input
                        break

                assert called_with_style, "render() should call st.markdown with a <style> block"


def test_render_log_workout_column_ratios():
    """Verify that the render_log_workout function uses the new column ratios."""
    # Mock workout plan
    workout_plan = {
        "schedule": {
            "Day 1": {
                "focus": "Full Body",
                "exercises": [{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
            }
        }
    }

    # Mock session state
    with patch("streamlit.session_state") as mock_state:
        mock_state.user_id = 1
        mock_state.exercise_logs = {}
        # Set return value for session_state.get() for session_timer_key and session_start_key
        mock_state.get.return_value = False

        with patch("streamlit.selectbox", return_value="Day 1"):
            with patch("streamlit.columns") as mock_columns:
                # Return mocks for each call to st.columns
                def columns_side_effect(ratios):
                    if len(ratios) == 3:
                        return (MagicMock(), MagicMock(), MagicMock())
                    else:
                        return (MagicMock(), MagicMock(), MagicMock(), MagicMock())

                mock_columns.side_effect = columns_side_effect

                # Mock components.v1.html to check its arguments
                with patch("streamlit.components.v1.html"):
                    # Mock the local imports from chat_pt.utils
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

                    # Check column ratios
                    # We expect st.columns([0.3, 0.7, 0.7, 0.5]) to be called
                    ratios_found = []
                    for call in mock_columns.call_args_list:
                        ratios_found.append(call[0][0])

                    assert [0.3, 0.7, 0.7, 0.5] in ratios_found

                    # Check if it was called twice with these ratios (header + data row)
                    count = sum(1 for r in ratios_found if r == [0.3, 0.7, 0.7, 0.5])
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
        if len(ratios) == 3:
            return (MagicMock(), MagicMock(), MagicMock())
        return (MagicMock(), MagicMock(), MagicMock(), MagicMock())

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
