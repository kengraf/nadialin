#!/bin/bash

# Function that accepts another function as an argument
test() {
    local func="$1"
    echo "Running function: $func"
    # Check if the function exists
    if declare -f "$func" > /dev/null; then
    # Call the function
        $func
        else
    echo "Function '$func' not found."
        fi
}

# Example function 1
example_one() {
    echo "This is example_one"
}

# Example function 2
example_two() {
    echo "This is example_two"
}

# Call test() with different functions as arguments
test example_one
test example_two
test non_existent_function
