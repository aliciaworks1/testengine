#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import platform


# -----------------------------
# Utilities
# -----------------------------

def run_command(command, cwd=None):
    print(f"\nRunning: {' '.join(command)}\n")
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def require_macos():
    if platform.system() != "Darwin":
        print("Apple platform builds require macOS.")
        sys.exit(1)


def require_windows():
    if platform.system() != "Windows":
        print("Windows build requires Windows.")
        sys.exit(1)


# -----------------------------
# Apple (Unified)
# -----------------------------

def apple_action(platform_name, clean=False):
    require_macos()

    action = "clean" if clean else "build"

    run_command([
        "xcodebuild",
        "-project", "apple/MyApp.xcodeproj",
        "-scheme", "MyApp",
        "-configuration", "Release",
        "-destination", f"generic/platform={platform_name}",
        action
    ])


# -----------------------------
# Android
# -----------------------------

def android_action(clean=False):
    gradle_path = os.path.join("android", "gradlew")

    if not os.path.exists(gradle_path):
        print("gradlew not found in android/")
        sys.exit(1)

    task = "clean" if clean else "assembleRelease"
    run_command([gradle_path, task], cwd="android")


# -----------------------------
# Windows
# -----------------------------

def windows_action(clean=False):
    require_windows()

    if clean:
        run_command([
            "msbuild",
            r"windows\MyApp.sln",
            "/t:Clean",
            "/p:Configuration=Release",
            "/p:Platform=x64"
        ])
    else:
        run_command([
            "msbuild",
            r"windows\MyApp.sln",
            "/p:Configuration=Release",
            "/p:Platform=x64"
        ])


# -----------------------------
# Main
# -----------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="build.py",
        description="Simple cross-platform build tool",
        epilog="""
Examples:
  python3 build.py --platform macos
  python3 build.py --platform ios --clean
  python3 build.py --platform android
  python3 build.py --platform windows --clean
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--platform",
        required=True,
        choices=["macos", "ios", "visionos", "android", "windows"],
        help="Target platform"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts instead of building"
    )

    args = parser.parse_args()

    if args.platform in ["macos", "ios", "visionos"]:
        apple_map = {
            "macos": "macOS",
            "ios": "iOS",
            "visionos": "visionOS",
        }
        apple_action(apple_map[args.platform], clean=args.clean)

    elif args.platform == "android":
        android_action(clean=args.clean)

    elif args.platform == "windows":
        windows_action(clean=args.clean)


if __name__ == "__main__":
    main()
