import os
import shutil
import argparse
from pathlib import Path

def generate_skeleton(project_path, engine_root, platform):
    print(f"Generating {platform} skeleton...")
    
    # Define Source based on platform type
    if platform == "apple":
        # Apple specifically uses the client runtime skeleton
        skeleton_src = engine_root / "runtime" / "client" / "skeleton"
    else:
        # Others use the standard platforms directory
        skeleton_src = engine_root / "platforms" / platform / "skeleton"

    # Destination is always project/build/platform
    build_dir = project_path / "build"
    skeleton_dest = build_dir / platform

    if not skeleton_src.exists():
        print(f"Note: No skeleton source found for {platform} at {skeleton_src}")
        return

    # Ensure build directory exists
    if not build_dir.exists():
        build_dir.mkdir(parents=True)

    # Copy skeleton structure
    try:
        shutil.copytree(skeleton_src, skeleton_dest, dirs_exist_ok=True)
    except Exception as e:
        print(f"Error copying {platform} skeleton: {e}")
        return
    
    # Placeholder replacement for skeleton configuration files
    project_name = project_path.name
    for root, dirs, files in os.walk(skeleton_dest):
        for file in files:
            file_path = Path(root) / file
            try:
                # Read file content and replace placeholders
                content = file_path.read_text(encoding="utf-8")
                new_content = content.replace("{{PROJECT_NAME}}", project_name)
                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                
                # Also rename the file itself if it contains the placeholder
                if "{{PROJECT_NAME}}" in file:
                    new_file_name = file.replace("{{PROJECT_NAME}}", project_name)
                    file_path.rename(file_path.parent / new_file_name)
                    
            except (UnicodeDecodeError, PermissionError):
                pass

def main():
    parser = argparse.ArgumentParser(description="Engine Project and Skeleton Generator")
    parser.add_argument("--name", required=True, help="Name of the new project")
    parser.add_argument("--template", default="default-3d", help="Template to use")
    # Allows user to specify platforms, defaults to apple
    parser.add_argument("--platforms", nargs="+", default=["apple"], help="Platforms to generate skeletons for")
    args = parser.parse_args()

    engine_root = Path(__file__).parent.parent
    project_path = engine_root / "projects" / args.name

    # 1. Check if project already exists
    if project_path.exists():
        print(f"Error: Project {args.name} already exists at {project_path}.")
        return

    # 2. Copy Template to Project Root
    print(f"Initializing project: {args.name}")
    template_path = engine_root / "templates" / args.template

    if not template_path.exists():
        print(f"Error: Template {template_path} not found.")
        return

    shutil.copytree(template_path, project_path, dirs_exist_ok=True)

    # 3. Generate Skeletons for each requested platform
    for platform in args.platforms:
        generate_skeleton(project_path, engine_root, platform)

    print(f"Success: Project {args.name} created.")

if __name__ == "__main__":
    main()