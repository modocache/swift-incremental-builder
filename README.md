# swift-incremental-builder

Don't use this. This is a small utility I use to experiment with Swift's
incremental compilation. It works best if you build Swift from source first:

```
$ git clone https://github.com/apple/swift.git
$ swift/utils/update-checkout --clone
$ swift/utils/build-script \
    --release \
    --build-swift-static-stdlib=1 \
    --build-swift-static-sdk-overlay=1
```

Then you can use this project to try building things incremetnally:

```
$ git clone https://github.com/modoache/swift-incremental-builder.git
$ cd swift-incremental-builder/fixtures/executable
$ python ../../main.py \
    --swift-root-build-dir /path/to/swift/build \
    *.swift \
    --swiftc-option="-driver-show-incremental" \
    --link executable
$ ./out/Main
x: 10
```

Or try the examples, which invoke swift-incremental-builder with the requisite
arguments to produce executables and more:

```
$ bash fixtures/executable/build.sh
$ bash fixtures/library/build.sh
$ bash fixtures/executable-with-library/build.sh
```

See the `--help` output for details:

```
$ python swift-incremental-builder/main.py --help
usage: main.py [-h] [--swift-root-build-dir SWIFT_ROOT_BUILD_DIR]
               [--swift-build-dir SWIFT_BUILD_DIR]
               [--output-module-name OUTPUT_MODULE_NAME] [--tmpdir TMPDIR]
               [--swiftc SWIFTC] [--target TARGET] [--outdir OUTDIR]
               [--output-file-map OUTPUT_FILE_MAP]
               [--swiftc-option [SWIFTC_OPTIONS [SWIFTC_OPTIONS ...]]]
               [--link] [--clang CLANG]
               [--xcode-developer-path XCODE_DEVELOPER_PATH]
               [--isysroot ISYSROOT]
               [--swift-static-sdk-path SWIFT_STATIC_SDK_PATH]
               input_files [input_files ...]

positional arguments:
  input_files           A list of files to compile incrementally and, if the
                        --link option is specified, to link into an
                        executable.

optional arguments:
  -h, --help            show this help message and exit
  --swift-root-build-dir SWIFT_ROOT_BUILD_DIR
                        The path to the build directory for a Swift source
                        build. This is used to derive the path to a swiftc
                        executable, Swift runtime libraries, and static Swift
                        runtime libraries used when linking. Instead of using
                        this option to infer these paths, the --swiftc,
                        --swift-sdk-path, and --swift-static-sdk-path options
                        may be used instead. This looks for a source build in
                        "/Users/bgesiak/local/Source/apple/build/Ninja-
                        ReleaseAssert" by default.
  --swift-build-dir SWIFT_BUILD_DIR
                        The path to a Swift build directory within the root
                        source build. If this is not provided, this script
                        attempts to find the the Swift build within the root
                        build directory specified with --swift-root-build-dir
                        option, for example "/path/to/build/swift-macosx-
                        x86_64".
  --output-module-name OUTPUT_MODULE_NAME
                        The name of the main Swift module and executable
                        that's produced by this script. "Main" by default.
  --tmpdir TMPDIR       The Swift compiler sometimes produces temporary files
                        during compilation, and places them in TMPDIR. This
                        option sets TMPDIR to a path of your choosing, and
                        sets that environment variable for each subcommand of
                        this script.
                        "/Users/bgesiak/Source/tmp/incremental/tmp" by
                        default.
  --swiftc SWIFTC       The path to a swiftc executable used to perform the
                        incremental compilation. If this is not provided, this
                        script attempts to find the the Swift build within the
                        build directory specified with --swift-build-dir
                        option, for example "/path/to/build/swift-macosx-
                        x86_64/bin/swiftc".
  --swiftc-option [SWIFTC_OPTIONS [SWIFTC_OPTIONS ...]]
                        Additional options to pass to the swiftc executable
                        when performing an incremental compilation. For
                        example, "-driver-show-incremental" prints information
                        about the steps the compiler is taking when performing
                        an incremental build.

Compilation options:
  Options for compiling the input files.

  --target TARGET       The -target passed to the Swift compiler invocation.
                        "x86_64-apple-macosx10.12" by default.
  --outdir OUTDIR       The directory at which to place incremental build
                        products. "/Users/bgesiak/Source/tmp/incremental/out"
                        by default.
  --output-file-map OUTPUT_FILE_MAP
                        Where to write the output file map to. /Users/bgesiak/
                        Source/tmp/incremental/OutputFileMap.json by default.

Linking options:
  Options for linking the input files.

  --link {executable,dylib}
                        If specified, link the Swift module produced by the
                        incremental compilation command into an "executable"
                        or a "dylib".
  --clang CLANG         The Clang executable to use in order to link the Swift
                        module into an executable. If this option is not
                        specified, this script attempts to find a Clang
                        executable built as part of a Swift source build, at
                        "/path/to/build/llvm-macosx-x86_64/bin/clang", for
                        example. "/Users/bgesiak/local/Source/apple/build
                        /Ninja-ReleaseAssert/llvm-macosx-x86_64/bin/clang" by
                        default.
  --xcode-developer-path XCODE_DEVELOPER_PATH
                        A sysroot needs to be provided when linking a Swift
                        module into an executable. This can be provided by
                        using the --isysroot option with this script. However,
                        if --isysroot is not provided, this script uses a
                        sysroot that exists within the Xcode installed at the
                        path specified by this option, which uses
                        "/Applications/Xcode_9.0.0_fb.app/Contents/Developer"
                        by default.
  --isysroot ISYSROOT   The sysroot to use when linking a Swift module into an
                        executable. If this option is not specified, then a
                        sysroot that exists within the Xcode specified by
                        --xcode-developer-path is used. By default, that's "/A
                        pplications/Xcode_9.0.0_fb.app/Contents/Developer/Plat
                        forms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk".
  --swift-static-sdk-path SWIFT_STATIC_SDK_PATH
                        The path to static builds of the Swift runtime
                        libraries. These are statically linked so that the
                        final executable can run without a DYLD_RUNTIME_PATH
                        specified. If this is not provided, this script
                        attempts to find static libraries within the Swift
                        source build directory specified with --swift-source-
                        build-dir, for example
                        "/path/to/build/lib/swift_static/macosx".

Example usage: after building Swift from source with static SDK libraries
enabled (`utils/build-script --release --build-swift-static-stdlib=1 --build-
swift-static-sdk-overlay=1`), run `main.py --swift-root-build-dir
~/path/to/swift/build foo.swift main.swift`
```
