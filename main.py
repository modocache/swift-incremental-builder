"""
Does some stuff.
"""

from __future__ import print_function

import argparse
import json
import os
import subprocess


DEFAULT_BUILD_DIRECTORY = os.path.join(
    os.path.expanduser('~'),
    'local',
    'Source',
    'apple',
    'build',
    'Ninja-ReleaseAssert',
)


def _get_xcode_select_path():
    return subprocess.check_output(['xcode-select', '-p']).strip()


def _get_default_isysroot_path(xcode_path):
    return os.path.join(
        xcode_path,
        'Platforms', 'MacOSX.platform', 'Developer', 'SDKs', 'MacOSX10.13.sdk',
    )


def _get_default_swift_build_path(build_dir):
    return os.path.join(build_dir, 'swift-macosx-x86_64')


def _get_default_swift_static_sdk_path(build_dir):
    return os.path.join(build_dir, 'lib', 'swift_static', 'macosx')


def _get_default_swiftc_path(build_dir):
    return os.path.join(build_dir, 'bin', 'swiftc')


def _get_default_clang_path(build_dir):
    return os.path.join(build_dir, 'llvm-macosx-x86_64', 'bin', 'clang')


def _run(cmd, env=os.environ.copy()):
    print('env TMPDIR={} '.format(env['TMPDIR']) + ' '.join(cmd) + '\n')
    subprocess.check_call(cmd, env=env)


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        epilog='Example usage: after building Swift from source with static '
               'SDK libraries enabled (`utils/build-script --release '
               '--build-swift-static-stdlib=1 '
               '--build-swift-static-sdk-overlay=1`), run `'
               '%(prog)s '
               '--swift-root-build-dir ~/path/to/swift/build '
               'foo.swift main.swift`',
    )
    parser.add_argument(
        'input_files',
        help='A list of files to compile incrementally and, if the --link '
             'option is specified, to link into an executable.',
        nargs='+',
    )
    parser.add_argument(
        '--swift-root-build-dir',
        help='The path to the build directory for a Swift source build. This '
             'is used to derive the path to a swiftc executable, Swift runtime '
             'libraries, and static Swift runtime libraries used when linking. '
             'Instead of using this option to infer these paths, the --swiftc, '
             '--swift-sdk-path, and --swift-static-sdk-path options may be '
             'used instead. This looks for a source build in "%(default)s" by '
             'default.',
        default=DEFAULT_BUILD_DIRECTORY,
    )
    parser.add_argument(
        '--swift-build-dir',
        help='The path to a Swift build directory within the root source '
             'build. If this is not provided, this script attempts to find the '
             'the Swift build within the root build directory specified with '
             '--swift-root-build-dir option, for example "{}".'.format(
                 _get_default_swift_build_path("/path/to/build/")),
    )
    parser.add_argument(
        '--output-module-name',
        help='The name of the main Swift module and executable that\'s '
             'produced by this script. "%(default)s" by default.',
        default='Main',
    )
    parser.add_argument(
        '--tmpdir',
        help='The Swift compiler sometimes produces temporary files during '
             'compilation, and places them in TMPDIR. This option sets TMPDIR '
             'to a path of your choosing, and sets that environment variable '
             'for each subcommand of this script. "%(default)s" by default.',
        default=os.path.join(os.getcwd(), 'tmp'),
    )

    compile_argument_group = parser.add_argument_group(
        'Compilation options',
        'Options for compiling the input files.',
    )
    parser.add_argument(
        '--swiftc',
        help='The path to a swiftc executable used to perform the incremental '
             'compilation. If this is not provided, this script attempts to '
             'find the the Swift build within the build directory specified '
             'with --swift-build-dir option, for example "{}".'.format(
                 _get_default_swiftc_path(
                     "/path/to/build/swift-macosx-x86_64")),
    )
    compile_argument_group.add_argument(
        '--target',
        help='The -target passed to the Swift compiler invocation. '
             '"%(default)s" by default.',
        default='x86_64-apple-macosx10.12',
    )
    compile_argument_group.add_argument(
        '--outdir',
        help='The directory at which to place incremental build products. '
             '"%(default)s" by default.',
        default=os.path.join(os.getcwd(), 'out'),
    )
    compile_argument_group.add_argument(
        '--output-file-map',
        help='Where to write the output file map to. %(default)s by default.',
        default=os.path.join(os.getcwd(), 'OutputFileMap.json'),
    )
    parser.add_argument(
        '--swiftc-option',
        help='Additional options to pass to the swiftc executable when '
             'performing an incremental compilation. For example, '
             '"-driver-show-incremental" prints information about the steps '
             'the compiler is taking when performing an incremental build.',
        action='append',
        default=[],
        dest='swiftc_options',
    )

    link_argument_group = parser.add_argument_group(
        'Linking options',
        'Options for linking the input files.',
    )
    link_argument_group.add_argument(
        '--link',
        help='If specified, link the Swift module produced by the incremental '
             'compilation command into an "executable" or a "dylib".',
        choices=['executable', 'dylib'],
    )
    link_argument_group.add_argument(
        '--clang',
        help='The Clang executable to use in order to link the Swift module '
             'into an executable. If this option is not specified, this script '
             'attempts to find a Clang executable built as part of a Swift '
             'source build, at "{}", for example. "%(default)s" by '
             'default.'.format(
                 _get_default_clang_path('/path/to/build')
             ),
        default=_get_default_clang_path(DEFAULT_BUILD_DIRECTORY),
    )
    link_argument_group.add_argument(
        '--xcode-developer-path',
        help='A sysroot needs to be provided when linking a Swift module into '
             'an executable. This can be provided by using the --isysroot '
             'option with this script. However, if --isysroot is not provided, '
             'this script uses a sysroot that exists within the Xcode '
             'installed at the path specified by this option, which uses '
             '"%(default)s" by default.',
        default=_get_xcode_select_path(),
    )
    link_argument_group.add_argument(
        '--isysroot',
        help='The sysroot to use when linking a Swift module into an '
             'executable. If this option is not specified, then a sysroot '
             'that exists within the Xcode specified by --xcode-developer-path '
             'is used. By default, that\'s "{}".'.format(
                 _get_default_isysroot_path(_get_xcode_select_path())),
    )
    link_argument_group.add_argument(
        '--swift-static-sdk-path',
        help='The path to static builds of the Swift runtime libraries. '
             'These are statically linked so that the final executable can run '
             'without a DYLD_RUNTIME_PATH specified. If this is not provided, '
             'this script attempts to find static libraries within the Swift '
             'source build directory specified with --swift-source-build-dir, '
             'for example "{}".'.format(
                 _get_default_swift_static_sdk_path("/path/to/build/")),
    )
    link_argument_group.add_argument(
        '--link-option',
        help='Additional options to pass to the linker when linking.',
        action='append',
        default=[],
        dest='linker_options',
    )

    args = parser.parse_args()

    env = os.environ.copy()
    env['TMPDIR'] = args.tmpdir
    env['DEVELOPER_DIR'] = '/Applications/Xcode_9.0.0_fb.app/Contents/Developer'
    env['SDKROOT'] = '/Applications/Xcode_9.0.0_fb.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk'

    # The Swift compiler asserts when it attempts to create temporary or
    # diagnostics files in directories that don't exist.
    _run(['mkdir', '-p', args.tmpdir], env)
    _run(['mkdir', '-p', args.outdir], env)

    # Normalize input files to absolute paths. This is important, as some
    # parts of the Swift driver use the path as an identifier for a file
    # when determining whether it's changed. So, for example, an incremental
    # build product for 'foo.swift' isn't used when compiling a file
    # '/tmp/foo.swift', even if they're actually the same file.
    input_files = [os.path.abspath(f) for f in args.input_files]

    # Generate the output file map.
    file_map = {
        "": {
            "swift-dependencies": os.path.join(
                args.outdir,
                '{}-master.swiftdeps'.format(args.output_module_name),
            ),
        },
    }
    object_files = []
    for input_file in input_files:
        file_base_name = os.path.splitext(os.path.basename(input_file))[0]
        object_file = os.path.join(args.outdir, '{}.o'.format(file_base_name))
        object_files.append(object_file)

        file_map[input_file] = {
            "swiftmodule": os.path.join(
                args.outdir,
                '{}~partial.swiftmodule'.format(file_base_name),
            ),
            "object": object_file,
            "llvm-bc": os.path.join(args.outdir, '{}.bc'.format(file_base_name)),
            "diagnostics": os.path.join(args.outdir, '{}.dia'.format(file_base_name)),
            "dependencies": os.path.join(args.outdir, '{}.d'.format(file_base_name)),
            "swift-dependencies": os.path.join(args.outdir, '{}.swiftdeps'.format(file_base_name)),
        }

    with open(args.output_file_map, 'w') as output_file:
        json.dump(file_map, output_file, ensure_ascii=False, sort_keys=True, indent=4)

    # Perform an incremental compilation.
    swift_build_dir = args.swift_build_dir
    if not swift_build_dir:
        swift_build_dir = _get_default_swift_build_path(args.swift_root_build_dir)
    swiftc = args.swiftc
    if not swiftc:
        swiftc = os.path.join(swift_build_dir, 'bin', 'swiftc')
    swiftmodule = os.path.join(
        args.outdir, '{}.swiftmodule'.format(args.output_module_name),
    )
    cmd = [
        swiftc, '-incremental',
        '-target', args.target,
        '-Onone',
        '-Xfrontend', '-serialize-debugging-options',
        '-c',
        '-j8',
    ] + input_files + [
        '-output-file-map', args.output_file_map,
        '-save-temps',
        '-serialize-diagnostics',
        '-emit-dependencies',
        '-emit-module',
        '-emit-module-path', swiftmodule,
        '-module-name', args.output_module_name,
        '-module-link-name', args.output_module_name,
    ]
    for option in args.swiftc_options:
        cmd += [option]
    _run(cmd, env)

    # Link.
    isysroot = args.isysroot
    if not isysroot:
        isysroot = os.path.join(
            args.xcode_developer_path,
            'Platforms', 'MacOSX.platform',
            'Developer', 'SDKs', 'MacOSX10.13.sdk',
        )
    swift_static_sdk_path = args.swift_static_sdk_path
    if not swift_static_sdk_path:
        swift_static_sdk_path = _get_default_swift_static_sdk_path(swift_build_dir)

    if args.link:
        cmd = [
            args.clang,
            '-arch', 'x86_64',
            '-isysroot', isysroot,
        ]
        if args.link == 'dylib':
            cmd += ['-dynamiclib']
        cmd += object_files + [
            '-L{}'.format(swift_static_sdk_path),
            '-lc++',
            '-framework', 'Foundation',
            '-Xlinker', '-add_ast_path', '-Xlinker', swiftmodule,
            '-Xlinker', '-dependency_info',
            '-Xlinker', os.path.join(
                args.outdir,
                '{}_dependency_info.dat'.format(args.output_module_name),
            ),
            '-o', os.path.join(args.outdir, args.output_module_name),
        ]
        for option in args.linker_options:
            cmd += [option]
        _run(cmd, env)


if __name__ == '__main__':
    main()
