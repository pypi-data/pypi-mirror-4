#!/bin/sh

cat <<EOF
  Checking translations for formal errors...
EOF

for translation in `ls *.po >/dev/null 2>&1`; do
    echo -e "\tChecking: $translation"
    msgfmt --check "$translation" || exit 1
done

cat <<EOF
  Translation check finished. Strings looking good.
EOF

