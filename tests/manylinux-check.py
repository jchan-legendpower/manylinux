# Logic copied from PEP 513, PEP 599

import sys


def is_manylinux1_compatible():
    # Only Linux, and only x86-64 / i686
    from sysconfig import get_platform

    if get_platform() not in ["linux-x86_64", "linux-i686"]:
        return False

    # Check for presence of _manylinux module
    try:
        import _manylinux

        return bool(_manylinux.manylinux1_compatible)
    except (ImportError, AttributeError):
        # Fall through to heuristic check below
        pass

    # Check glibc version. CentOS 5 uses glibc 2.5.
    return have_compatible_glibc(2, 5)


def is_manylinux2010_compatible():
    # Only Linux, and only x86-64 / i686
    from sysconfig import get_platform

    if get_platform() not in ["linux-x86_64", "linux-i686"]:
        return False

    # Check for presence of _manylinux module
    try:
        import _manylinux

        return bool(_manylinux.manylinux2010_compatible)
    except (ImportError, AttributeError):
        # Fall through to heuristic check below
        pass

    # Check glibc version. CentOS 6 uses glibc 2.12.
    return have_compatible_glibc(2, 12)


def is_manylinux2014_compatible():
    # Only Linux, and only supported architectures
    from sysconfig import get_platform

    if get_platform() not in [
        "linux-x86_64",
        "linux-i686",
        "linux-aarch64",
        "linux-armv7l",
        "linux-ppc64",
        "linux-ppc64le",
        "linux-s390x",
        "linux-riscv64",
    ]:
        return False

    # Check for presence of _manylinux module
    try:
        import _manylinux

        return bool(_manylinux.manylinux2014_compatible)
    except (ImportError, AttributeError):
        # Fall through to heuristic check below
        pass

    # Check glibc version. CentOS 7 uses glibc 2.17.
    # PEP 513 contains an implementation of this function.
    return have_compatible_glibc(2, 17)


def have_compatible_glibc(major, minimum_minor):
    import ctypes

    process_namespace = ctypes.CDLL(None)
    try:
        gnu_get_libc_version = process_namespace.gnu_get_libc_version
    except AttributeError:
        # Symbol doesn't exist -> therefore, we are not linked to
        # glibc.
        return False

    # Call gnu_get_libc_version, which returns a string like "2.5".
    gnu_get_libc_version.restype = ctypes.c_char_p
    version_str = gnu_get_libc_version()
    # py2 / py3 compatibility:
    if not isinstance(version_str, str):
        version_str = version_str.decode("ascii")

    # Parse string and check against requested version.
    version = [int(piece) for piece in version_str.split(".")]
    assert len(version) == 2
    if major != version[0]:
        return False
    return minimum_minor <= version[1]


exit_code = 0

if sys.argv[2] in {"x86_64", "i686"} and (
    sys.argv[1] in {"manylinux1", "manylinux2010", "manylinux2014"}
    or sys.argv[1].startswith("manylinux_")
):
    if is_manylinux1_compatible():
        print(f"{sys.argv[1]} {sys.executable} is manylinux1 compatible")
    else:
        print(f"{sys.argv[1]} {sys.executable} is NOT manylinux1 compatible")
        exit_code = 1

if sys.argv[2] in {"x86_64", "i686"} and (
    sys.argv[1] in {"manylinux2010", "manylinux2014"} or sys.argv[1].startswith("manylinux_")
):
    if is_manylinux2010_compatible():
        print(f"{sys.argv[1]} {sys.executable} is manylinux2010 compatible")
    else:
        print(f"{sys.argv[1]} {sys.executable} is NOT manylinux2010 compatible")
        exit_code = 1

if sys.argv[1] in {"manylinux2014"} or sys.argv[1].startswith("manylinux_"):
    if is_manylinux2014_compatible():
        print(f"{sys.argv[1]} {sys.executable} is manylinux2014 compatible")
    else:
        print(f"{sys.argv[1]} {sys.executable}  is NOT manylinux2014 compatible")
        exit_code = 1

sys.exit(exit_code)
