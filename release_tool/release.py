"""Main release logic."""

import sys
from .config import Config
from .latex_build import build_latex
from .git_operations import (
    check_on_main_branch,
    check_up_to_date,
    is_latest_commit_released,
    check_tag_validity,
    create_github_release,
    verify_release_on_latest_commit,
    GitError,
    GitHubError,
)


def prompt_user(prompt: str) -> str:
    """
    Prompt user for input.

    Args:
        prompt: Prompt message

    Returns:
        User input (stripped)
    """
    return input(f"{prompt}: ").strip()


def run_release() -> int:
    """
    Main release process.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Load configuration
        print("⚙️  Loading configuration...")
        config = Config()
        print(f"✓ Project root: {config.project_root}")
        print(f"✓ Main branch: {config.main_branch}")

        # Build LaTeX
        build_latex(config.latex_dir)

        # Check git status
        print("\n🔍 Checking git repository status...")
        check_on_main_branch(config.project_root, config.main_branch)
        print(f"✓ On {config.main_branch} branch")

        check_up_to_date(config.project_root, config.main_branch)

        # Check if latest commit already has a release
        is_released, latest_release = is_latest_commit_released(config.project_root)

        if is_released:
            print(
                f"\n✓ Latest commit already has a release: "
                f"{latest_release['tagName']}"
            )
            print("Nothing to do. Exiting.")
            return 0

        # Display latest release info
        print("\n📋 Current release status:")
        if latest_release:
            print(f"  Last release: {latest_release['tagName']}")
            if latest_release.get('name'):
                print(f"  Title: {latest_release['name']}")
            if latest_release.get('body'):
                # Show first 100 chars of release notes
                body = latest_release['body']
                body_preview = body[:100] + "..." if len(body) > 100 else body
                print(f"  Notes: {body_preview}")
        else:
            print("  No releases found (this will be the first release)")

        # Prompt for new release
        print("\n📝 Creating new release...")
        while True:
            new_tag = prompt_user("Enter new tag name (e.g., v1.0.0)")
            if new_tag:
                break
            print("Tag name cannot be empty")

        release_title = prompt_user(
            f"Enter release title (press Enter to use '{new_tag}')"
        )
        if not release_title:
            release_title = new_tag
            print(f"Using default title: {release_title}")

        release_notes = prompt_user(
            "Enter release notes (press Enter to skip)"
        )
        if not release_notes:
            release_notes = ""
            print("No release notes provided")

        # Verify tag validity before creating release
        print("\n🔍 Verifying tag validity...")
        check_tag_validity(config.project_root, new_tag, config.main_branch)

        # Create GitHub release (automatically creates tag and pushes)
        create_github_release(
            config.project_root,
            new_tag,
            release_title,
            release_notes
        )

        # Final verification
        print("\n🔍 Final verification...")
        check_up_to_date(config.project_root, config.main_branch)
        verify_release_on_latest_commit(config.project_root, new_tag)

        print(f"\n✅ Release {new_tag} completed successfully!")
        return 0

    except (GitError, GitHubError, RuntimeError, FileNotFoundError) as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Release cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1
