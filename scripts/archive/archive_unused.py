#!/usr/bin/env python3
"""
Archive Unused Files Script

A generic tool to identify and archive unused files in a project.
Files are considered "used" if they are:
1. Setup files (devcontainer.json, requirements, scripts, configs)
2. Referenced in .devcontainer/devcontainer.json
3. Referenced in labs.md
4. Referenced in README.md
5. Referenced in any remaining files after the above conditions

Unused files are moved to an 'archive' directory using 'git mv' for safe recovery.
A detailed log of all actions is written for auditing.

Usage:
    python scripts/archive_unused.py [--dry-run] [--verbose]

Options:
    --dry-run   Show what would be archived without actually moving files
    --verbose   Show detailed information about file analysis
"""

import os
import re
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Set


class UnusedFileArchiver:
    # Directories/patterns to always exclude from archiving
    ALWAYS_EXCLUDE = {
        '.git',
        '.devcontainer',
        'archive',  # Don't archive the archive itself
        '__pycache__',
        '.venv',
        'venv',
        'py_env',
        'node_modules',
        '.vscode',
        '.idea',
        '.github',
    }

    # File patterns that are always considered "setup" files
    SETUP_PATTERNS = {
        'devcontainer.json',
        'requirements.txt',
        'requirements',
        'package.json',
        'package-lock.json',
        'pyproject.toml',
        'setup.py',
        'setup.cfg',
        'Makefile',
        'Dockerfile',
        'docker-compose.yml',
        'docker-compose.yaml',
        '.gitignore',
        '.gitattributes',
        '.env',
        '.env.example',
        'LICENSE',
        'CHANGELOG.md',
        'CONTRIBUTING.md',
    }

    # File extensions that indicate setup/config files
    SETUP_EXTENSIONS = {
        '.sh',  # Shell scripts are typically setup
        '.toml',
        '.cfg',
        '.ini',
        '.conf',
    }

    # Primary reference files to check
    PRIMARY_REF_FILES = [
        '.devcontainer/devcontainer.json',
        'labs.md',
        'README.md',
    ]

    def __init__(self, project_root: str, dry_run: bool = False, verbose: bool = False):
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.archive_dir = self.project_root / 'archive'
        self.log_lines = []
        self.used_files: Set[Path] = set()
        self.all_files: Set[Path] = set()

    def log(self, message: str, level: str = "INFO"):
        """Log a message to both console and log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_lines.append(log_entry)
        if self.verbose or level in ("INFO", "WARNING", "ERROR"):
            print(log_entry)

    def debug(self, message: str):
        """Log debug message (only shown in verbose mode)."""
        if self.verbose:
            self.log(message, "DEBUG")

    def is_excluded_path(self, path: Path) -> bool:
        """Check if a path should be excluded from consideration."""
        parts = path.relative_to(self.project_root).parts
        for part in parts:
            if part in self.ALWAYS_EXCLUDE:
                return True
            if part.startswith('.') and part not in ('.gitignore', '.gitattributes', '.env', '.env.example'):
                return True
        return False

    def is_setup_file(self, path: Path) -> bool:
        """Check if a file is a setup/config file."""
        name = path.name
        suffix = path.suffix.lower()

        # Check exact filename matches
        if name.lower() in {p.lower() for p in self.SETUP_PATTERNS}:
            return True

        # Check if in a setup-related directory
        rel_path = path.relative_to(self.project_root)
        parts = rel_path.parts
        if parts and parts[0].lower() in ('scripts', 'requirements', '.devcontainer', 'tools'):
            return True

        # Check extensions
        if suffix in self.SETUP_EXTENSIONS:
            return True

        return False

    def get_all_project_files(self) -> Set[Path]:
        """Get all files in the project, excluding ignored directories."""
        files = set()
        for root, dirs, filenames in os.walk(self.project_root):
            # Modify dirs in-place to prevent walking into excluded directories
            dirs[:] = [d for d in dirs if d not in self.ALWAYS_EXCLUDE and not d.startswith('.')]

            for filename in filenames:
                filepath = Path(root) / filename
                if not self.is_excluded_path(filepath):
                    files.add(filepath)
        return files

    def extract_references(self, file_path: Path) -> Set[str]:
        """Extract file references from a file's content."""
        references = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.debug(f"Could not read {file_path}: {e}")
            return references

        # Common patterns for file references
        patterns = [
            # Markdown image/link syntax: ![text](path) or [text](path)
            r'\[.*?\]\(\.?/?([^)]+)\)',
            # HTML src/href attributes
            r'(?:src|href)=["\']\.?/?([^"\']+)["\']',
            # Import/require statements
            r'(?:import|require|from)\s+["\']\.?/?([^"\']+)["\']',
            # Shell script paths
            r'(?:bash|python|sh|source)\s+\.?/?([^\s;]+)',
            # Generic quoted paths that look like files
            r'["\']\.?/?([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)["\']',
            # Unquoted paths after common commands
            r'(?:code|cat|cp|mv|rm|ls)\s+\.?/?([^\s;|&]+)',
            # postCreateCommand, postAttachCommand patterns
            r'Command":\s*"[^"]*?([a-zA-Z0-9_\-./]+\.(?:sh|py|js))',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.strip().strip('"\'')
                # Skip URLs and anchors
                if clean_match.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                # Remove query strings and anchors from paths (e.g., image.png?raw=true)
                clean_match = re.split(r'[?#]', clean_match)[0]
                # Skip very short matches or those with special chars
                if len(clean_match) < 2 or any(c in clean_match for c in '<>{}[]'):
                    continue
                references.add(clean_match)

        return references

    def resolve_reference(self, reference: str, source_file: Path) -> Path | None:
        """Try to resolve a reference to an actual file path."""
        # Try relative to source file's directory
        source_dir = source_file.parent
        candidates = [
            source_dir / reference,
            self.project_root / reference,
            self.project_root / reference.lstrip('./'),
        ]

        for candidate in candidates:
            try:
                resolved = candidate.resolve()
                if resolved.exists() and resolved.is_file():
                    return resolved
            except Exception:
                continue
        return None

    def find_file_by_name(self, filename: str) -> list[Path]:
        """Find all files matching a filename (without directory path)."""
        matches = []
        # Strip any directory prefix and extension variations
        base_name = Path(filename).name
        # Also try adding common extensions
        extensions_to_try = ['', '.py', '.js', '.ts', '.md', '.txt', '.json']

        for file_path in self.all_files:
            file_base = file_path.name
            # Direct match
            if file_base == base_name:
                matches.append(file_path)
            # Match without extension (e.g., "classic_calc" matches "classic_calc.py")
            elif any(file_base == base_name + ext for ext in extensions_to_try):
                matches.append(file_path)
            # Match stem (filename without extension)
            elif file_path.stem == Path(base_name).stem:
                matches.append(file_path)
        return matches

    def mark_file_used(self, file_path: Path, reason: str):
        """Mark a file as used with a reason."""
        if file_path not in self.used_files:
            self.used_files.add(file_path)
            self.debug(f"Marked as used: {file_path.relative_to(self.project_root)} ({reason})")

    def analyze_references_from_file(self, source_file: Path, reason_prefix: str) -> Set[Path]:
        """Analyze a file and find all files it references."""
        newly_found = set()
        references = self.extract_references(source_file)

        for ref in references:
            # First try exact path resolution
            resolved = self.resolve_reference(ref, source_file)
            if resolved and resolved in self.all_files and resolved not in self.used_files:
                self.mark_file_used(resolved, f"{reason_prefix}: {source_file.name}")
                newly_found.add(resolved)
            else:
                # Try fuzzy filename matching (for references like "classic_calc" without path)
                matches = self.find_file_by_name(ref)
                for match in matches:
                    if match in self.all_files and match not in self.used_files:
                        self.mark_file_used(match, f"{reason_prefix} (by name): {source_file.name}")
                        newly_found.add(match)

        return newly_found

    def run_analysis(self):
        """Run the complete analysis to identify unused files."""
        self.log("Starting unused file analysis...")
        self.log(f"Project root: {self.project_root}")

        # Step 1: Get all project files
        self.all_files = self.get_all_project_files()
        self.log(f"Found {len(self.all_files)} total files to analyze")

        # Step 2: Mark setup files as used
        setup_count = 0
        for file_path in self.all_files:
            if self.is_setup_file(file_path):
                self.mark_file_used(file_path, "setup file")
                setup_count += 1
        self.log(f"Marked {setup_count} setup/config files as used")

        # Step 3: Analyze primary reference files
        for ref_file in self.PRIMARY_REF_FILES:
            full_path = self.project_root / ref_file
            if full_path.exists():
                self.mark_file_used(full_path, "primary reference file")
                self.analyze_references_from_file(full_path, f"referenced in {ref_file}")
                self.log(f"Analyzed references from {ref_file}")
            else:
                self.debug(f"Primary reference file not found: {ref_file}")

        # Step 4: Iteratively find references from used files
        iteration = 0
        max_iterations = 50  # Prevent infinite loops

        while iteration < max_iterations:
            iteration += 1
            files_to_check = list(self.used_files)
            new_refs_found = 0

            for file_path in files_to_check:
                if file_path.suffix in ('.py', '.js', '.ts', '.md', '.json', '.yaml', '.yml', '.html', '.txt'):
                    newly_found = self.analyze_references_from_file(file_path, "transitive reference")
                    new_refs_found += len(newly_found)

            if new_refs_found == 0:
                break

            self.debug(f"Iteration {iteration}: found {new_refs_found} new referenced files")

        self.log(f"Reference analysis complete after {iteration} iterations")
        self.log(f"Total used files: {len(self.used_files)}")

        # Calculate unused files
        unused_files = self.all_files - self.used_files
        self.log(f"Unused files identified: {len(unused_files)}")

        return unused_files

    def archive_files(self, unused_files: Set[Path]):
        """Archive unused files using git mv."""
        if not unused_files:
            self.log("No files to archive")
            return

        # Create archive directory if needed
        if not self.dry_run:
            self.archive_dir.mkdir(exist_ok=True)

        archived_count = 0
        failed_count = 0

        for file_path in sorted(unused_files):
            rel_path = file_path.relative_to(self.project_root)
            dest_path = self.archive_dir / rel_path

            if self.dry_run:
                self.log(f"[DRY-RUN] Would archive: {rel_path}")
                archived_count += 1
                continue

            # Create destination directory structure
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Use git mv to preserve history
            try:
                result = subprocess.run(
                    ['git', 'mv', str(file_path), str(dest_path)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"Archived: {rel_path} -> archive/{rel_path}")
                    archived_count += 1
                else:
                    # If git mv fails (file not tracked), use regular mv
                    self.debug(f"git mv failed, trying regular move: {result.stderr}")
                    import shutil
                    shutil.move(str(file_path), str(dest_path))
                    self.log(f"Moved (untracked): {rel_path} -> archive/{rel_path}")
                    archived_count += 1
            except Exception as e:
                self.log(f"Failed to archive {rel_path}: {e}", "ERROR")
                failed_count += 1

        self.log(f"Archive complete: {archived_count} files archived, {failed_count} failures")

    def write_log(self):
        """Write the audit log to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"archive_log_{timestamp}.txt"
        log_path = self.archive_dir / log_filename

        if self.dry_run:
            log_path = self.project_root / f"archive_dry_run_{timestamp}.txt"

        # Add summary to log
        self.log_lines.insert(0, "=" * 60)
        self.log_lines.insert(1, "UNUSED FILE ARCHIVE LOG")
        self.log_lines.insert(2, f"Project: {self.project_root}")
        self.log_lines.insert(3, f"Date: {datetime.now().isoformat()}")
        self.log_lines.insert(4, f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        self.log_lines.insert(5, "=" * 60)
        self.log_lines.insert(6, "")

        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'w') as f:
                f.write('\n'.join(self.log_lines))
            print(f"\nLog written to: {log_path}")
        except Exception as e:
            print(f"Failed to write log: {e}")

    def run(self):
        """Run the complete archive process."""
        self.log("=" * 60)
        self.log("Starting Unused File Archiver")
        self.log(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        self.log("=" * 60)

        # Verify we're in a git repository
        git_dir = self.project_root / '.git'
        if not git_dir.exists():
            self.log("Warning: Not a git repository. Files will be moved instead of git mv'd", "WARNING")

        # Run analysis
        unused_files = self.run_analysis()

        # Show summary before archiving
        if unused_files:
            self.log("\nUnused files to be archived:")
            for f in sorted(unused_files):
                rel_path = f.relative_to(self.project_root)
                self.log(f"  - {rel_path}")

        # Archive files
        self.archive_files(unused_files)

        # Write log
        self.write_log()

        return len(unused_files)


def main():
    parser = argparse.ArgumentParser(
        description='Archive unused files in a project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be archived without actually moving files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information about file analysis'
    )
    parser.add_argument(
        '--project-root', '-p',
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Resolve project root
    project_root = Path(args.project_root).resolve()

    archiver = UnusedFileArchiver(
        project_root=str(project_root),
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    unused_count = archiver.run()

    if args.dry_run:
        print(f"\n[DRY-RUN] Would archive {unused_count} files")
        print("Run without --dry-run to actually archive files")
    else:
        print(f"\nArchived {unused_count} files to 'archive' directory")

    return 0 if unused_count >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
