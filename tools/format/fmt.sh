
#!/bin/bash

set -e

find CM7/src -iname '*.h' -o -iname '*.c' | xargs clang-format -i
find CM7/lib -iname '*.h' -o -iname '*.c' | xargs clang-format -i
find CM7/include -iname '*.h' -o -iname '*.c' | xargs clang-format -i