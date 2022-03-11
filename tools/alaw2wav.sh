#!/bin/bash
#
# Convfert a-law encoding audio to wav audio
# Example: ffmpeg -f alaw -ar 8000 -i FRFRA_20080622-210025-01_outLine.alaw FRFRA_20080622-210025-01_outLine.wav
#
# Zhenhao Ge, 2022-01-25

dataset=FRF_ASR002 # FRF_ASR001, FRF_ASR002
FROM_DIR="${HOME}/Data/ots_french/${dataset}/Audio"
TO_DIR="${HOME}/Data/ots_french/${dataset}/Audio"

# sanity check for directories
[ ! -d ${FROM_DIR} ] && echo "Error: not exist ${FROM_DIR}"
[ ! -d ${TO_DIR} ] && mkdir -p ${TO_DIR} && echo "Creating ${TO_DIR} ..."

# specify the source and destination file extensions
ext1=".alaw"
ext2=".wav"

sr=8000

# get audio files
wav_files=($(find "${FROM_DIR}" -name "*${ext1}" | sort))
nwavs=${#wav_files[@]}

# print # of wav files
echo "# of wavs in ${FROM_DIR}: ${nwavs}"

for (( i=0; i<nwavs; i++ )); do

  # get the source filename
  f=${wav_files[$i]}

  f2=$(echo $f | sed "s|${FROM_DIR}|${TO_DIR}|g") # substitute path
  f2=${f2%.*}${ext2} # replace ext

  # create the destination dir
  dest_dir=$(dirname $f2)
  [ ! -d ${dest_dir} ] && mkdir -p ${dest_dir}

  # convert source file to destination file
  if [ ! -f ${f2} ]; then
    echo "$f -> $f2 "
    ffmpeg -f alaw -ar ${sr} -i $f $f2
  else
    echo "Destination file already exist: $f2"
  fi

done
