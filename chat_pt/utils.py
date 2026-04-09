import re
from typing import Any, Dict, List, Tuple, Union


def group_exercises_by_sequence(
    exercises: List[Dict[str, Any]],
) -> Dict[Union[int, str], List[Tuple[int, Dict[str, Any]]]]:
    """
    Group exercises by their sequence number to identify supersets.

    Args:
    ----
        exercises: List of exercise dictionaries.

    Returns:
    -------
        A dictionary mapping sequence keys to lists of (original_index, exercise) tuples.
        Sequence keys are integers for grouped exercises (supersets) or strings
        like 'solo_i' for standalone exercises.

    """
    sequence_groups = {}
    for i, exercise in enumerate(exercises):
        sequence = exercise.get("sequence")
        seq_num = None

        if sequence:
            # Extract numeric part (e.g., "2A" -> 2, "3B" -> 3, "1" -> 1)
            match = re.match(r"(\d+)", str(sequence))
            if match:
                seq_num = int(match.group(1))

        if seq_num is not None:
            if seq_num not in sequence_groups:
                sequence_groups[seq_num] = []
            sequence_groups[seq_num].append((i, exercise))
        else:
            # Standalone exercise without a valid sequence number
            sequence_groups[f"solo_{i}"] = [(i, exercise)]

    return sequence_groups


def get_sorted_sequence_keys(sequence_groups: Dict[Union[int, str], Any]) -> List[Union[int, str]]:
    """
    Sort sequence keys so that numeric keys (supersets) come first or in order,
    followed by solo exercises based on their original index.
    """
    numeric_keys = sorted([k for k in sequence_groups.keys() if isinstance(k, int)])
    string_keys = [k for k in sequence_groups.keys() if isinstance(k, str)]

    # Further sort string keys if they follow 'solo_i' pattern
    def solo_sort_key(k):
        if k.startswith("solo_"):
            try:
                return int(k.split("_")[1])
            except (IndexError, ValueError):
                return float("inf")
        return k

    string_keys.sort(key=solo_sort_key)

    return numeric_keys + string_keys
