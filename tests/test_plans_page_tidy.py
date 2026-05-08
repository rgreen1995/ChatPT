from unittest.mock import MagicMock, patch

from chat_pt.plans_page import render


def test_plans_page_css_injection():
    """Verify that the plans page injects the expected CSS for tidy buttons."""
    with patch("streamlit.session_state") as mock_state:
        mock_state.user_id = 1
        # Mock consultations to avoid empty state early return
        mock_consultations = [{"id": 1, "completed": True, "created_at": "2023-01-01"}]

        with patch("chat_pt.plans_page.get_user_consultations", return_value=mock_consultations):
            with patch("chat_pt.plans_page.get_workout_plan", return_value={"schedule": {}}):
                with patch("chat_pt.plans_page.get_conversation_history", return_value=[]):
                    with patch("streamlit.markdown") as mock_markdown:
                        with patch("streamlit.selectbox", return_value=0):
                            render()

                            # Check if markdown was called with a style block
                            called_with_style = False
                            for call in mock_markdown.call_args_list:
                                arg = call[0][0]
                                if "<style>" in arg:
                                    called_with_style = True
                                    # Verify key parts of the minimal, non-intrusive CSS.
                                    assert "/* Button tightening (safe, global) */" in arg
                                    assert ".stButton button {" in arg
                                    assert "min-height: 2.4rem !important;" in arg
                                    # flex overrides must be scoped to the marker class,
                                    # not applied globally to every stHorizontalBlock.
                                    assert (
                                        'div[data-testid="stHorizontalBlock"]:has(.plans-exercise-meta)'
                                        in arg
                                    )
                                    # Global (unscoped) overrides that hurt mobile layout must stay absent.
                                    assert "overflow-x: hidden !important" not in arg
                                    assert "max-width: 100vw !important" not in arg
                                    break

                            assert (
                                called_with_style
                            ), "render() should call st.markdown with a <style> block"


def test_plans_page_column_ratios():
    """Verify that the exercise rows in plans page use the updated column ratios."""
    # Mock workout plan with a day and an exercise
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
        mock_consultations = [{"id": 1, "completed": True, "created_at": "2023-01-01"}]

        with patch("chat_pt.plans_page.get_user_consultations", return_value=mock_consultations):
            with patch("chat_pt.plans_page.get_workout_plan", return_value=workout_plan):
                with patch("chat_pt.plans_page.get_conversation_history", return_value=[]):
                    with patch("streamlit.tabs") as mock_tabs:
                        # Mock tabs to return a list of mocks
                        mock_tab = MagicMock()
                        mock_tabs.return_value = [mock_tab]

                        with patch("streamlit.selectbox", return_value=0):
                            with patch("streamlit.columns") as mock_columns:
                                # Return mocks for each call to st.columns
                                def columns_side_effect(ratios):
                                    if isinstance(ratios, list):
                                        return [MagicMock() for _ in range(len(ratios))]
                                    return [MagicMock() for _ in range(ratios)]

                                mock_columns.side_effect = columns_side_effect

                                # We need to ensure we enter the "with day_tab" block
                                # Since zip(day_tabs, sorted_schedule.items()) is used

                                render()

                                # Check column ratios for exercise row.
                                # Mobile layout fix: each exercise now uses a two-row layout.
                                # Row 1 is the exercise name (no columns); row 2 uses
                                # [2, 2, 1, 1] for meta | rest | swap | info.
                                ratios_found = []
                                for call in mock_columns.call_args_list:
                                    if isinstance(call[0][0], list):
                                        ratios_found.append(call[0][0])

                                assert [2, 2, 1, 1] in ratios_found
                                # The old wide-name single-row ratio must no longer be used.
                                assert [4, 2, 1.5, 1.5] not in ratios_found
