set -e
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

python ../../main.py \
    foo.swift \
    --link dylib \
    --output-module-name Foo \
    --tmpdir foo-tmp \
    --outdir foo-out \
    --swiftc-option="-emit-library" \
    $*

mv \
    libFoo.dylib \
    foo-out/libFoo.dylib

python ../../main.py \
    main.swift \
    --link executable \
    --tmpdir main-tmp \
    --outdir main-out \
    --swiftc-option="-Ifoo-out" \
    --link-option="-Lfoo-out" \
    --link-option="-lFoo" \
    $*

DYLD_LIBRARY_PATH=foo-out ./main-out/Main
