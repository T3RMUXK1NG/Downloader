# Cross-Platform Build Systems Reference

## Supported Platforms

| Platform | Architectures | Binary Format | Build Tool |
|----------|--------------|---------------|------------|
| Windows | x86, x64 | .exe | PyInstaller, Go build |
| Linux | x86, x64, ARM, ARM64 | ELF | PyInstaller, Go build, Cargo |
| macOS | x64, ARM64 (M1/M2) | Mach-O | PyInstaller, Go build, Cargo |
| Android | ARM, ARM64, x86 | .apk | Buildozer, Chaquopy |
| Termux | ARM, ARM64, x86 | Binary | PyInstaller (Termux) |
| iOS | ARM64 | .ipa | (Jailbreak required) |

## Python Build System

```python
import os
import subprocess
import shutil
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class BuildConfig:
    name: str
    version: str
    entry_point: str
    icon: Optional[str] = None
    hidden_imports: List[str] = None
    data_files: List[tuple] = None
    one_file: bool = True
    console: bool = True
    platform: str = None
    arch: str = None

class PythonBuilder:
    """Build Python applications for multiple platforms."""
    
    PLATFORM_CONFIGS = {
        'windows-x64': {
            'pyinstaller_args': ['--target-platform', 'windows'],
            'ext': '.exe'
        },
        'linux-x64': {
            'pyinstaller_args': [],
            'ext': ''
        },
        'linux-arm64': {
            'pyinstaller_args': [],
            'ext': ''
        },
        'macos-x64': {
            'pyinstaller_args': [],
            'ext': ''
        },
        'macos-arm64': {
            'pyinstaller_args': [],
            'ext': ''
        }
    }
    
    def __init__(self, config: BuildConfig):
        self.config = config
    
    async def build(self, platform: str, arch: str, output_dir: str) -> str:
        """Build for specific platform and architecture."""
        config_key = f"{platform}-{arch}"
        platform_config = self.PLATFORM_CONFIGS.get(config_key, {})
        
        output_name = f"{self.config.name}_{platform}_{arch}{platform_config.get('ext', '')}"
        output_path = os.path.join(output_dir, output_name)
        
        # Build PyInstaller command
        cmd = ['pyinstaller']
        
        if self.config.one_file:
            cmd.append('--onefile')
        
        if self.config.console:
            cmd.append('--console')
        else:
            cmd.append('--noconsole')
        
        if self.config.icon:
            cmd.extend(['--icon', self.config.icon])
        
        for imp in (self.config.hidden_imports or []):
            cmd.extend(['--hidden-import', imp])
        
        for src, dst in (self.config.data_files or []):
            cmd.extend(['--add-data', f"{src}{os.pathsep}{dst}"])
        
        cmd.extend(['--name', output_name])
        cmd.extend(['--distpath', output_dir])
        cmd.append(self.config.entry_point)
        
        # Run build
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise BuildError(f"Build failed: {stderr.decode()}")
        
        return output_path
    
    async def build_all(self, output_dir: str) -> Dict[str, str]:
        """Build for all platforms."""
        results = {}
        
        for platform_arch in self.PLATFORM_CONFIGS.keys():
            platform, arch = platform_arch.rsplit('-', 1)
            try:
                results[platform_arch] = await self.build(platform, arch, output_dir)
            except BuildError as e:
                results[platform_arch] = f"Failed: {e}"
        
        return results

class BuildError(Exception):
    pass
```

## Go Build System

```python
class GoBuilder:
    """Build Go applications for multiple platforms."""
    
    PLATFORMS = {
        'windows-x64': {'goos': 'windows', 'goarch': 'amd64', 'ext': '.exe'},
        'windows-x86': {'goos': 'windows', 'goarch': '386', 'ext': '.exe'},
        'linux-x64': {'goos': 'linux', 'goarch': 'amd64', 'ext': ''},
        'linux-arm64': {'goos': 'linux', 'goarch': 'arm64', 'ext': ''},
        'linux-arm': {'goos': 'linux', 'goarch': 'arm', 'ext': ''},
        'macos-x64': {'goos': 'darwin', 'goarch': 'amd64', 'ext': ''},
        'macos-arm64': {'goos': 'darwin', 'goarch': 'arm64', 'ext': ''}
    }
    
    def __init__(self, name: str, version: str, source_dir: str):
        self.name = name
        self.version = version
        self.source_dir = source_dir
    
    async def build(self, platform: str, output_dir: str) -> str:
        """Build for specific platform."""
        config = self.PLATFORMS[platform]
        
        output_name = f"{self.name}_{platform}{config['ext']}"
        output_path = os.path.join(output_dir, output_name)
        
        env = os.environ.copy()
        env['GOOS'] = config['goos']
        env['GOARCH'] = config['goarch']
        env['CGO_ENABLED'] = '0'
        
        # Add version info
        ldflags = f"-s -w -X main.Version={self.version}"
        
        cmd = [
            'go', 'build',
            '-ldflags', ldflags,
            '-o', output_path,
            '.'
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.source_dir,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise BuildError(f"Go build failed: {stderr.decode()}")
        
        return output_path
    
    async def build_all(self, output_dir: str) -> Dict[str, str]:
        """Build for all platforms."""
        results = {}
        
        for platform in self.PLATFORMS:
            try:
                results[platform] = await self.build(platform, output_dir)
            except BuildError as e:
                results[platform] = f"Failed: {e}"
        
        return results
```

## Rust Build System

```python
class RustBuilder:
    """Build Rust applications for multiple platforms."""
    
    TARGETS = {
        'windows-x64': 'x86_64-pc-windows-gnu',
        'linux-x64': 'x86_64-unknown-linux-gnu',
        'linux-arm64': 'aarch64-unknown-linux-gnu',
        'macos-x64': 'x86_64-apple-darwin',
        'macos-arm64': 'aarch64-apple-darwin'
    }
    
    def __init__(self, name: str, version: str, source_dir: str):
        self.name = name
        self.version = version
        self.source_dir = source_dir
    
    async def setup_targets(self):
        """Install required targets."""
        for target in set(self.TARGETS.values()):
            await asyncio.create_subprocess_exec(
                'rustup', 'target', 'add', target
            )
    
    async def build(self, platform: str, output_dir: str) -> str:
        """Build for specific platform."""
        target = self.TARGETS.get(platform)
        if not target:
            raise BuildError(f"Unsupported platform: {platform}")
        
        ext = '.exe' if 'windows' in platform else ''
        output_name = f"{self.name}_{platform}{ext}"
        
        cmd = [
            'cargo', 'build',
            '--release',
            '--target', target
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.source_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise BuildError(f"Rust build failed: {stderr.decode()}")
        
        # Copy binary to output
        binary_name = f"{self.name}{ext}"
        src_path = os.path.join(
            self.source_dir, 'target', target, 'release', binary_name
        )
        dst_path = os.path.join(output_dir, output_name)
        shutil.copy(src_path, dst_path)
        
        return dst_path
```

## Release Packager

```python
class ReleasePackager:
    """Create release packages with all binaries."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    async def create_release(self, binaries: Dict[str, str], output_dir: str) -> str:
        """Create release package."""
        release_name = f"{self.name}_v{self.version}"
        release_dir = os.path.join(output_dir, release_name)
        os.makedirs(release_dir, exist_ok=True)
        
        # Copy binaries
        for platform, binary_path in binaries.items():
            if os.path.exists(binary_path):
                shutil.copy(binary_path, release_dir)
        
        # Create checksums
        checksums = self._generate_checksums(release_dir)
        with open(os.path.join(release_dir, 'checksums.txt'), 'w') as f:
            f.write(checksums)
        
        # Create release notes
        release_notes = self._generate_release_notes()
        with open(os.path.join(release_dir, 'RELEASE_NOTES.md'), 'w') as f:
            f.write(release_notes)
        
        # Create archive
        archive_path = shutil.make_archive(release_dir, 'zip', release_dir)
        
        return archive_path
    
    def _generate_checksums(self, directory: str) -> str:
        """Generate SHA256 checksums."""
        checksums = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                sha256 = hashlib.sha256()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
                checksums.append(f"{sha256.hexdigest()}  {filename}")
        return '\n'.join(checksums)
    
    def _generate_release_notes(self) -> str:
        """Generate release notes."""
        return f"""# {self.name} v{self.version}

## Downloads

| Platform | Architecture | Binary |
|----------|-------------|--------|
| Windows | x64 | {self.name}_windows-x64.exe |
| Linux | x64 | {self.name}_linux-x64 |
| Linux | ARM64 | {self.name}_linux-arm64 |
| macOS | x64 | {self.name}_macos-x64 |
| macOS | ARM64 (M1/M2) | {self.name}_macos-arm64 |

## Installation

### Linux/macOS
```bash
chmod +x {self.name}_*
./{self.name}_linux-x64
```

### Windows
Run the .exe file directly.

## Verification

Verify checksums using:
```bash
sha256sum -c checksums.txt
```
"""
```

## Build Configuration

```yaml
# build.yaml
tool:
  name: security-scanner
  version: 1.0.0
  entry_point: src/main.py

build:
  python:
    enabled: true
    one_file: true
    console: true
    hidden_imports:
      - rich
      - requests
      - asyncio
  
  go:
    enabled: false
  
  rust:
    enabled: false

platforms:
  - windows-x64
  - linux-x64
  - linux-arm64
  - macos-x64
  - macos-arm64

release:
  create_archive: true
  generate_checksums: true
  create_release_notes: true
```
