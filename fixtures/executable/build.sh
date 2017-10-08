set -e
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

python ../../main.py \
    *.swift \
    --link executable \
    $*

./out/Main
