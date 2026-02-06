#!/usr/bin/env zsh

if (( $# != 1 )); then
  echo "Usage: $0 /folder"
  exit 1
fi

root="$1"

for obj in "$root"/**/*.obj(N); do
  echo "Cleaning $obj"

  # create temp file
  tmp="${obj}.tmp"

  # remove lines:
  # - starting with #
  # - mtllib
  # - object name from scaniverse
  sed '/^#/d; /^mtllib /d; /^o Scaniverse/d' "$obj" > "$tmp"

  mv "$tmp" "$obj"
done

echo "Done."
