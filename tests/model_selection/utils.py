import re
from typing import Union

import pytest

from skfp.model_selection.utils import (
    ensure_nonempty_subset,
    get_data_from_indices,
    split_additional_data,
    validate_train_test_split_sizes,
    validate_train_valid_test_split_sizes,
)


@pytest.fixture
def smiles_data() -> list[str]:
    return ["CCC", "CCCl", "CCO", "CCN"]


@pytest.fixture
def additional_data() -> list[list[Union[str, int, bool]]]:
    return [["a", "b", "c", "d"], [1, 2, 3, 4], [True, False, True, False]]


def test_ensure_nonempty_subset_passes():
    ensure_nonempty_subset([1, 2, 3], "Test")


def test_ensure_nonempty_subset_raises_error():
    with pytest.raises(ValueError, match="Train subset is empty"):
        ensure_nonempty_subset([], "Train")


def test_validate_train_test_split_sizes_both_provided():
    assert validate_train_test_split_sizes(0.7, 0.3, 10) == (7, 3)


def test_validate_train_test_split_sizes_train_missing():
    assert validate_train_test_split_sizes(None, 0.3, 10) == (7, 3)


def test_validate_train_test_split_sizes_test_missing():
    assert validate_train_test_split_sizes(0.6, None, 10) == (6, 4)


def test_validate_train_test_split_sizes_both_missing():
    assert validate_train_test_split_sizes(None, None, 10) == (8, 2)


def test_validate_train_test_split_sizes_not_sum_to_one():
    with pytest.raises(ValueError, match="train_size and test_size must sum to 1.0"):
        validate_train_test_split_sizes(0.6, 0.5, 10)


def test_get_data_from_indices_valid(smiles_data):
    result = get_data_from_indices(smiles_data, [0, 2])
    assert result == ["CCC", "CCO"]


def test_get_data_from_indices_duplicates(smiles_data):
    # This works since we iterate over a set of indices
    result = get_data_from_indices(smiles_data, [0, 2, 2])
    assert result == ["CCC", "CCO"]


def test_get_data_from_indices_empty(smiles_data):
    result = get_data_from_indices(smiles_data, [])
    assert result == []


def test_get_data_from_indices_out_of_range(smiles_data):
    with pytest.raises(IndexError):
        get_data_from_indices(smiles_data, [0, 4])


def test_get_data_from_indices_mixed_types(smiles_data):
    result = get_data_from_indices(smiles_data, [0, 1, 2, 3])
    assert result == ["CCC", "CCCl", "CCO", "CCN"]


def test_split_additional_data(additional_data):
    result = split_additional_data(additional_data, [0, 2])
    assert result == [["a", "c"], [1, 3], [True, True]]


def test_split_additional_data_multiple_indices(additional_data):
    result = split_additional_data(additional_data, [0, 1], [2, 3])
    assert result == [
        ["a", "b"],
        ["c", "d"],
        [1, 2],
        [3, 4],
        [True, False],
        [True, False],
    ]


def test_split_additional_data_varying_lists_lengths(additional_data):
    result = split_additional_data(additional_data, [1], [0, 3])
    assert result == [["b"], ["a", "d"], [2], [1, 4], [False], [True, False]]


def test_split_additional_data_multiple_empty_indice_list(additional_data):
    result = split_additional_data(additional_data, [], [])
    assert result == [[], [], [], [], [], []]


def test_validate_train_valid_test_split_sizes_all_provided():
    result = validate_train_valid_test_split_sizes(0.7, 0.2, 0.1, 10)
    assert result == (7, 2, 1)


def test_validate_train_valid_test_split_sizes_not_sum_to_one():
    with pytest.raises(
        ValueError,
        match="The sum of train_size, valid_size, and test_size must be 1.0.",
    ):
        validate_train_valid_test_split_sizes(0.7, 0.2, 0.2, 10)


def test_validate_train_valid_test_split_sizes_missing_values():
    with pytest.raises(
        ValueError,
        match="All of the sizes must be provided",
    ):
        validate_train_valid_test_split_sizes(0.7, None, 0.2, 10)


def test_validate_train_valid_test_split_sizes_all_missing():
    result = validate_train_valid_test_split_sizes(None, None, None, 10)
    assert result == (8, 1, 1)


def test_validate_train_test_split_sizes_different_type():
    with pytest.raises(
        TypeError,
        match="train_size and test_size must be of the same type, got <class 'int'> "
        "for train_size and <class 'float'> for test_size",
    ):
        validate_train_test_split_sizes(7, 0.3, 10)


def test_validate_train_valid_test_split_sizes_different_type():
    with pytest.raises(
        TypeError,
        match=re.escape(
            "All sizes must be of the same type, got: [<class 'int'>, <class 'float'>, <class 'int'>]"
        ),
    ):
        validate_train_valid_test_split_sizes(6, 0.3, 1, 10)


def test_validate_train_test_split_sizes_train_size_too_large():
    with pytest.raises(
        ValueError,
        match="train_size as an integer must be smaller than data_length, got 11 for data_length 10",
    ):
        validate_train_test_split_sizes(11, 1, 10)


def test_validate_train_test_split_sizes_test_size_too_large():
    with pytest.raises(
        ValueError,
        match="test_size as an integer must be smaller than data_length, got 11 for data_length 10",
    ):
        validate_train_test_split_sizes(1, 11, 10)


def test_validate_train_test_split_sizes_train_size_zero():
    with pytest.raises(ValueError, match="train_size is 0.0"):
        validate_train_test_split_sizes(0.0, 1.0, 10)


def test_validate_train_test_split_sizes_test_size_zero():
    with pytest.raises(ValueError, match="test_size is 0.0"):
        validate_train_test_split_sizes(1.0, 0.0, 10)


def test_validate_train_valid_test_split_sizes_invalid_type():
    with pytest.raises(
        TypeError,
        match=re.escape(
            "All sizes must be either int or float, got: [<class 'int'>, <class 'str'>, <class 'float'>]"
        ),
    ):
        validate_train_valid_test_split_sizes(6, "invalid", 1.0, 10)


def test_validate_train_valid_test_split_sizes_sum_not_equal_data_length_incorrect_total():
    with pytest.raises(
        ValueError,
        match="The sum of train_size, valid_size, and test_size must equal data_length, got 12 instead",
    ):
        validate_train_valid_test_split_sizes(5, 3, 4, 13)
