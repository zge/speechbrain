#!/bin/bash
#
# Count duration for CommonVoice data
#
# Zhenhao Ge, 2022-03-11

DATA_DIR=$HOME/Data/CommonVoice/cv-corpus-8.0-2022-01-19/

ext=".mp3"
audiofiles=($(find "${DATA_DIR}" -name "*${ext}" | sort))
nfiles=${#audiofiles[@]}

# print # of wav files
echo "# of audio files in ${DATA_DIR}: ${nfiles}"

dur=0
for (( i=0; i<${nfiles}; i++ )); do

  if [ $(expr $i % 1000) == "0" ]; then
      echo "processing $(($i+1)) - $(($i+1000)) ..."
  fi

  # get the filename
  f=${audiofiles[$i]}
  
  # get the duration
  hms=$(soxi -d $f)
  sec=$(echo $hms | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
  dur=$(echo $dur+$sec | bc)

done
