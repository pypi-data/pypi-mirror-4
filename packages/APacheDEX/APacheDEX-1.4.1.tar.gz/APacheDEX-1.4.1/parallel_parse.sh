#!/bin/bash
usage() {
  echo "Usage:"
  echo "  find [...] -print0 | $0 \\"
  echo "    parallelism state_dir out_file command [arg1 [...]]"
  echo "Reads filenames to process from stdin, null-delimited."
}

if [ $1 = '-h' -o $1 = '--help' ]; then
  usage
  exit 0
fi

PARALLELISM=$1
shift
STATE_DIR=$1
mkdir -p "$STATE_DIR" || exit $?
shift
OUT_FILE=$1
shift

if [ $# -eq 0 ]; then
  usage
  exit 1
fi

# XXX: any simpler way ?
xargs -0 -r -n 1 -P $PARALLELISM -I "@FILE@" -- "$SHELL" -c 'INFILE="$1";shift;STATE_DIR="$1";shift;echo -n .;"$@" -Q --format json --out "$STATE_DIR/$(sed s:/:@:g <<< "$INFILE").json" "$INFILE"' "$0" "@FILE@" "$STATE_DIR" "$@"
echo
"$@" --out "$OUT_FILE" --state-file "$STATE_DIR"/*
