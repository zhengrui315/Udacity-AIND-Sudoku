
from utils import *
import heapq
import operator


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
unitlist = unitlist + [[rows[i] + cols[i] for i in range(9)]] + [[rows[::-1][i] + cols[i] for i in range(9)]]


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes) # a dict from box to units that the box belongs to
peers = extract_peers(units, boxes) # a dict from box to all other boxes that share a unit with the box


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # TODO: Implement this function!
    twins = set()
    
    for unit_id,unit in enumerate(unitlist):
        two = [(box,values[box]) for box in unit if len(values[box])==2]
        two = sorted(two,key=lambda tup: tup[1])
        for i in range(len(two)-1):
            q = []
            if two[i][1] == two[i+1][1] and two[i][1] not in q:
                q.append(two[i][1])
                twins.add((unit_id,two[i][0],two[i+1][0],two[i][1])) # tuple = (unit_id,box1,box2,box_value)

    for unit_id,box1,box2,value in twins:
        for box in unitlist[unit_id]:
            if box in [box1,box2]:
                continue
            values[box] = values[box].replace(value[0],'')
            values[box] = values[box].replace(value[1],'')

    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # TODO: Copy your code from the classroom to complete this function
    box = [b for b in values.keys() if len(values[b]) ==1]
    for b in box:
        for peer in peers[b]:
            values[peer] = values[peer].replace(values[b],'')
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # TODO: Copy your code from the classroom to complete this function
    for unit in unitlist:
        for i in range(9):
            count = [1 if str(i+1) in values[unit[idx]] else 0 for idx in range(9)]
            if sum(count) == 1:
                idx = count.index(1)
                values[unit[idx]] = str(i+1)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # TODO: Copy your code from the classroom and modify it to complete this function
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        
        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        # call naked_twins
        values = naked_twins(values)
        
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # TODO: Copy your code from the classroom to complete this function
    
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    
    # the only two cases the search returns is when a decision is reaches, false or solution
    if not values:
        return False
    if len([box for box in values.keys() if len(values[box]) ==1]) == 9**2:
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    _, box = min((len(values[box]),box) for box in values.keys() if len(values[box])>1)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!

    for value in values[box]:
        values_copy = values.copy()
        values_copy[box] = value
        values_copy2 = search(values_copy)
        
        #if a solution (not false) is returned, return the solution; if false, continue the loop
        if values_copy2:
            return values_copy2

def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
