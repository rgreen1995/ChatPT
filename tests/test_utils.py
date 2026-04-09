from chat_pt.utils import get_sorted_sequence_keys, group_exercises_by_sequence


def test_group_exercises_by_sequence():
    """Test grouping exercises by their sequence number."""
    exercises = [
        {"name": "Squat", "sequence": "1"},
        {"name": "Bench Press", "sequence": "2A"},
        {"name": "Row", "sequence": "2B"},
        {"name": "Deadlift", "sequence": "3"},
        {"name": "Plank"},  # No sequence
    ]

    groups = group_exercises_by_sequence(exercises)
    sorted_keys = get_sorted_sequence_keys(groups)

    # Assertions
    assert 1 in groups
    assert 2 in groups
    assert 3 in groups
    assert "solo_4" in groups

    assert len(groups[1]) == 1
    assert len(groups[2]) == 2
    assert len(groups[3]) == 1
    assert len(groups["solo_4"]) == 1

    assert groups[2][0][1]["name"] == "Bench Press"
    assert groups[2][1][1]["name"] == "Row"

    assert sorted_keys == [1, 2, 3, "solo_4"]


def test_mixed_sequence_formats():
    """Test grouping with mixed sequence formats (int, str, invalid)."""
    exercises = [
        {"name": "A", "sequence": 1},
        {"name": "B", "sequence": "1"},
        {"name": "C", "sequence": "2A"},
        {"name": "D", "sequence": "X"},  # Invalid numeric
    ]

    groups = group_exercises_by_sequence(exercises)
    sorted_keys = get_sorted_sequence_keys(groups)

    assert 1 in groups
    assert len(groups[1]) == 2
    assert 2 in groups
    assert len(groups[2]) == 1
    assert "solo_3" in groups

    assert sorted_keys == [1, 2, "solo_3"]
