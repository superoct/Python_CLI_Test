#!/bin/bash

# Command to send

COMMAND_FILE="files_to_process/${1}_${2}.txt"
STOP_COMMAND_FILE="files_to_process/stop_${1}_${2}.txt"
FOLDER_NAME=$1
FILE_NAME=$2

cleanup() {
	echo "stop $FOLDER_NAME $FILE_NAME" >> $STOP_COMMAND_FILE
	echo "Script Interrupt."
	exit 1
}

trap cleanup SIGINT

echo "start $FOLDER_NAME $FILE_NAME" >> $COMMAND_FILE
echo "Command sent: start $FOLDER_NAME $FILE_NAME"

while true; do
	if [ -f "output_${FOLDER_NAME}_${FILE_NAME}.txt" ]; then
		echo "Output for ${FOLDER_NAME}_${FILE_NAME} received: $(cat output_${FOLDER_NAME}_${FILE_NAME}.txt)"
		rm "output_${FOLDER_NAME}_${FILE_NAME}.txt"
		break
	fi
	sleep 1
done
