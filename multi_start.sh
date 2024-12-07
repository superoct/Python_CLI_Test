#!/bin/bash

arg_pairs=(
	"test1 file1"
	"test2 file2"
	"test3 file3"
	"test4 file4"
	"test5 file5"
	"test6 file6"
	"test7 file7"
	"test8 file8"
	"test9 file9"
	"test10 file10"
	"test11 file11"
	"test12 file12"
	"test13 file13"
	"test14 file14"
	"test15 file15"
)

start_script_path="./start.sh"

run_script() {
	local arg1=$1
	local arg2=$2
	echo "Running $start_script_path with arguments: $arg1 $arg2"
	bash "$start_script_path" "$arg1" "$arg2"

}

for pair in "${arg_pairs[@]}"; do
	set -- $pair
	arg1=$1
	arg2=$2

	run_script "$arg1" "$arg2" &

done

wait

echo "All calls to $start_script_path completed successfully."
