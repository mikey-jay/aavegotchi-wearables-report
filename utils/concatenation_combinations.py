import itertools

def get_n_length_concatenation_combinations(x, y, n):
    # get all concatenations of x + y that contains combinations of n elements of x paired with all possible permutations of y
    permutations = []
    x_combinations = list(itertools.combinations(x, n))
    y_permutations = list(itertools.product(y, repeat=n))
    for x_combination in x_combinations:
        for y_permutation in y_permutations:
            permutations.append(list(tuple(a + b for a, b in zip(x_combination, y_permutation))))
    return permutations

# tests
if __name__ == '__main__':
    assert get_n_length_concatenation_combinations(['a'], ['1'], 1) == [['a1']]
    assert get_n_length_concatenation_combinations(['a', 'b'], ['1'], 1) == [['a1'],['b1']]
    assert ['b2'] in get_n_length_concatenation_combinations(['a', 'b'], ['1', '2'], 1)

    length_2_result = get_n_length_concatenation_combinations(['a', 'b'], ['1', '2'], 2)

    assert len(length_2_result[0]) == 2
    assert ['a1', 'a1'] not in length_2_result
    assert ['a1', 'b2'] in length_2_result

    length_3_result = get_n_length_concatenation_combinations(['a', 'b', 'c'], ['1', '2', '3'], 3)
    assert len(length_3_result[3]) == 3

    assert len(get_n_length_concatenation_combinations(['a', 'b', 'c'], ['1', '2'], 2)) == 12