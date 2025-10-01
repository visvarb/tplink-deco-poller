#!/usr/bin/env python3

"""
TPLink Deco Poller Bootstrap Script
Download this single file and run it to automatically:
1. Download all required files from GitHub
2. Set up the environment
3. Run the initial generation

Usage:
    wget https://raw.githubusercontent.com/visvarb/tplink-deco-poller/main/bootstrap.py
    sudo python3 bootstrap.py

Or:
    curl -O https://raw.githubusercontent.com/visvarb/tplink-deco-poller/main/bootstrap.py
    sudo python3 bootstrap.py
"""

import os
import sys
import subprocess
import shutil
import venv
import tempfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional
import json

# Configuration - Update these URLs to match your GitHub repository
GITHUB_REPO = "visvarb/tplink-deco-poller"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Files to download from GitHub
REQUIRED_FILES = {
    "generate_hosts.py": "generate_hosts.py",
    "run_generate_hosts.sh": "run_generate_hosts.sh", 
    "requirements.txt": "requirements.txt"
}

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def log_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def log_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

class TPLinkBootstrap:
    def __init__(self):
        self.base_dir = Path("/srv/tplink-deco")
        self.venv_dir = self.base_dir / "venv"
        self.log_dir = self.base_dir / "log"
        self.temp_dir = None
        
    def check_privileges(self) -> bool:
        """Check if running with sufficient privileges"""
        if os.geteuid() != 0:
            log_error("This script must be run as root or with sudo")
            return False
        return True
    
    def check_internet_connection(self) -> bool:
        """Check if we can connect to GitHub"""
        try:
            log_info("Checking internet connection...")
            urllib.request.urlopen("https://github.com", timeout=10)
            log_success("Internet connection verified")
            return True
        except urllib.error.URLError:
            log_error("No internet connection or GitHub is not accessible")
            return False
    
    def update_packages(self) -> bool:
        """Update system packages if needed"""
        try:
            log_info("Checking if package update is needed...")
            
            # Check if apt update was run recently (within last hour)
            apt_cache = Path("/var/cache/apt/pkgcache.bin")
            if apt_cache.exists():
                import time
                last_update = apt_cache.stat().st_mtime
                if time.time() - last_update < 3600:  # 1 hour
                    log_info("Package list was updated recently, skipping apt update")
                    return True
            
            log_info("Updating package lists...")
            subprocess.run(["apt", "update"], check=True, capture_output=True)
            log_success("Package lists updated")
            return True
            
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to update packages: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during package update: {e}")
            return False
    
    def install_system_dependencies(self) -> bool:
        """Install required system packages"""
        packages = ["python3", "python3-venv", "python3-dev", "python3-pip", "curl", "wget", "pip"]
        
        try:
            log_info("Checking system dependencies...")
            
            # Check which packages need to be installed
            to_install = []
            for package in packages:
                result = subprocess.run(
                    ["dpkg", "-l"], 
                    capture_output=True, text=True
                )
                if f"ii  {package} " not in result.stdout:
                    to_install.append(package)
                else:
                    log_info(f"{package} is already installed")
            
            if to_install:
                log_info(f"Installing packages: {', '.join(to_install)}")
                subprocess.run(
                    ["apt", "install", "-y"] + to_install,
                    check=True
                )
                log_success("System dependencies installed successfully")
            else:
                log_success("All required system packages are already installed")
            
            return True
            
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to install system dependencies: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during dependency installation: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Create required directories"""
        try:
            log_info("Creating required directories...")
            
            directories = [self.base_dir, self.log_dir]
            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    log_success(f"Created directory: {directory}")
                else:
                    log_info(f"Directory already exists: {directory}")
            
            return True
            
        except Exception as e:
            log_error(f"Failed to create directories: {e}")
            return False
    
    def download_files(self) -> bool:
        """Download all required files from GitHub"""
        try:
            log_info("Downloading files from GitHub...")
            
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp())
            
            downloaded_files = {}
            
            for local_name, github_name in REQUIRED_FILES.items():
                url = f"{GITHUB_RAW_BASE}/{github_name}"
                local_path = self.temp_dir / local_name
                
                log_info(f"Downloading {github_name} from {url}")
                
                try:
                    urllib.request.urlretrieve(url, local_path)
                    downloaded_files[local_name] = local_path
                    log_success(f"Downloaded {github_name}")
                except urllib.error.URLError as e:
                    log_error(f"Failed to download {github_name}: {e}")
                    return False
            
            # Copy downloaded files to destination
            for local_name, temp_path in downloaded_files.items():
                dest_path = self.base_dir / local_name
                
                # Create backup if destination exists and is different
                if dest_path.exists():
                    import filecmp
                    if not filecmp.cmp(temp_path, dest_path, shallow=False):
                        import datetime
                        backup_name = f"{local_name}.backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        backup_path = self.base_dir / backup_name
                        shutil.copy2(dest_path, backup_path)
                        log_info(f"Created backup of existing {local_name}")
                
                shutil.copy2(temp_path, dest_path)
                log_success(f"Installed {local_name}")
            
            return True
            
        except Exception as e:
            log_error(f"Failed to download files: {e}")
            return False
        finally:
            # Clean up temporary directory
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
    
    def setup_virtual_environment(self) -> bool:
        """Create and setup Python virtual environment"""
        try:
            log_info("Setting up Python virtual environment...")
            
            # Create virtual environment if it doesn't exist
            if not self.venv_dir.exists():
                log_info(f"Creating virtual environment at {self.venv_dir}")
                venv.create(self.venv_dir, with_pip=True)
                log_success("Virtual environment created")
            else:
                log_info(f"Virtual environment already exists at {self.venv_dir}")
            
            # Get pip path
            pip_path = self.venv_dir / "bin" / "pip"
            
            # Upgrade pip
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install packages from requirements.txt
            requirements_file = self.base_dir / "requirements.txt"
            if requirements_file.exists():
                log_info(f"Installing packages from requirements.txt...")
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                             check=True, capture_output=True)
                log_success("Packages installed successfully")
            else:
                log_warning("Requirements file not found, installing tplinkrouterc6u directly")
                subprocess.run([str(pip_path), "install", "tplinkrouterc6u>=5.4.0"], 
                             check=True, capture_output=True)
                log_success("tplinkrouterc6u installed successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to setup virtual environment: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during virtual environment setup: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create environment configuration file"""
        try:
            env_file = self.base_dir / "tplink.env"
            
            if not env_file.exists():
                log_info("Creating environment file template...")
                
                env_content = """# TPLink Deco Configuration
# Replace the values below with your actual router settings

# Router gateway IP address (e.g., 192.168.1.1 or 10.1.0.1)
TPLINK_GATEWAY=your_router_gateway_ip_address

# Router admin password
TPLINK_PASSWORD=your_router_password

# Optional: Enable testing mode (1 for testing, 0 for production)
# TESTING=0
"""
                env_file.write_text(env_content)
                log_success(f"Created environment file template: {env_file}")
                log_warning(f"Please edit {env_file} and set your actual router credentials")
            else:
                log_info(f"Environment file already exists: {env_file}")
            
            return True
            
        except Exception as e:
            log_error(f"Failed to create environment file: {e}")
            return False
    
    def set_permissions(self) -> bool:
        """Set proper file and directory permissions"""
        try:
            log_info("Setting proper permissions...")
            
            # Set ownership
            shutil.chown(self.base_dir, user="root", group="root")
            
            # Set directory permissions
            self.base_dir.chmod(0o755)
            self.log_dir.chmod(0o755)
            
            if self.venv_dir.exists():
                self.venv_dir.chmod(0o755)
                python_exe = self.venv_dir / "bin" / "python"
                if python_exe.exists():
                    python_exe.chmod(0o755)
            
            # Set file permissions
            files_permissions = {
                "generate_hosts.py": 0o644,
                "tplink.env": 0o600,
                "run_generate_hosts.sh": 0o755,
                "requirements.txt": 0o644
            }
            
            for filename, perms in files_permissions.items():
                filepath = self.base_dir / filename
                if filepath.exists():
                    filepath.chmod(perms)
            
            log_success("Permissions set correctly")
            return True
            
        except Exception as e:
            log_error(f"Failed to set permissions: {e}")
            return False
    
    def setup_cron(self) -> bool:
        """Setup cron job for automatic execution"""
        try:
            log_info("Setting up cron job...")
            
            cron_job = "0 * * * * /srv/tplink-deco/run_generate_hosts.sh"
            
            # Get current crontab
            try:
                result = subprocess.run(["crontab", "-l"], 
                                      capture_output=True, text=True)
                current_crontab = result.stdout
            except subprocess.CalledProcessError:
                current_crontab = ""
            
            # Check if job already exists
            if cron_job in current_crontab:
                log_info("Cron job already exists")
                return True
            
            # Add the job
            new_crontab = current_crontab.rstrip() + "\n" + cron_job + "\n"
            
            process = subprocess.Popen(["crontab", "-"], 
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            if process.returncode == 0:
                log_success("Cron job added successfully")
                return True
            else:
                log_error("Failed to add cron job")
                return False
                
        except Exception as e:
            log_error(f"Failed to setup cron job: {e}")
            return False
    
    def configure_credentials(self) -> bool:
        """Interactive configuration of router credentials"""
        env_file = self.base_dir / "tplink.env"
        
        try:
            log_info("Router credentials configuration...")
            
            # Check if already configured
            if env_file.exists():
                env_content = env_file.read_text()
                if ("your_router_gateway_ip_address" not in env_content and 
                    "your_router_password" not in env_content):
                    log_info("Credentials appear to already be configured")
                    return True
            
            print("\n" + "="*50)
            print("ROUTER CREDENTIALS CONFIGURATION")
            print("="*50)
            
            gateway = input("Enter your router gateway IP (e.g., 192.168.1.1 or 10.1.0.1): ").strip()
            if not gateway:
                log_warning("No gateway provided, keeping template values")
                return True
            
            import getpass
            password = getpass.getpass("Enter your router admin password: ").strip()
            if not password:
                log_warning("No password provided, keeping template values")
                return True
            
            # Update environment file
            env_content = f"""# TPLink Deco Configuration
# Generated by bootstrap script

# Router gateway IP address
TPLINK_GATEWAY={gateway}

# Router admin password
TPLINK_PASSWORD={password}

# Optional: Enable testing mode (1 for testing, 0 for production)
# TESTING=0
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            log_success("Credentials configured successfully")
            return True
            
        except KeyboardInterrupt:
            log_warning("\nConfiguration interrupted, keeping template values")
            return True
        except Exception as e:
            log_error(f"Failed to configure credentials: {e}")
            return False
    
    def run_initial_generation(self) -> bool:
        """Run the hosts generation script for the first time"""
        try:
            log_info("Running initial hosts generation...")
            
            env_file = self.base_dir / "tplink.env"
            if not env_file.exists():
                log_warning("Environment file not found, skipping initial generation")
                return True
            
            # Check if credentials are configured
            env_content = env_file.read_text()
            if ("your_router_gateway_ip_address" in env_content or 
                "your_router_password" in env_content):
                log_warning("Credentials not configured, skipping initial generation")
                log_info("Please edit /srv/tplink-deco/tplink.env and run: sudo /srv/tplink-deco/run_generate_hosts.sh")
                return True
            
            # Run the generation script
            script_path = self.base_dir / "run_generate_hosts.sh"
            result = subprocess.run([str(script_path)], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                log_success("Initial hosts generation completed successfully")
                
                # Show log output
                log_file = self.log_dir / "output.log"
                if log_file.exists():
                    log_info("Generation log (last 10 lines):")
                    lines = log_file.read_text().strip().split('\n')
                    for line in lines[-10:]:
                        print(f"  {line}")
                
                # Show hosts file
                hosts_file = Path("/etc/hosts")
                if hosts_file.exists():
                    log_info("Updated hosts file:")
                    print("  " + "="*40)
                    print(hosts_file.read_text())
                    print("  " + "="*40)
                
                return True
            else:
                log_error("Initial generation failed")
                if result.stderr:
                    log_error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            log_error("Initial generation timed out")
            return False
        except Exception as e:
            log_error(f"Failed to run initial generation: {e}")
            return False
    
    def show_summary(self):
        """Show installation summary and next steps"""
        print("\n" + "="*60)
        log_success("TPLink Deco Poller Bootstrap Complete!")
        print("="*60)
        
        log_info("Installation Summary:")
        print(f"  • Base directory: {self.base_dir}")
        print(f"  • Virtual environment: {self.venv_dir}")
        print(f"  • Log directory: {self.log_dir}")
        print(f"  • Configuration file: {self.base_dir}/tplink.env")
        
        print("\n" + "Next Steps:")
        print("  1. Check configuration: sudo nano /srv/tplink-deco/tplink.env")
        print("  2. Run manually: sudo /srv/tplink-deco/run_generate_hosts.sh")
        print("  3. Check logs: tail -f /srv/tplink-deco/log/output.log")
        print("  4. View hosts file: cat /etc/hosts")
        
        print("\n" + "Automation:")
        print("  • Script runs automatically every hour via cron")
        print("  • Check cron jobs: crontab -l")
        
        print("\n" + "Files Downloaded:")
        for local_name in REQUIRED_FILES.keys():
            file_path = self.base_dir / local_name
            status = "✓" if file_path.exists() else "✗"
            print(f"  {status} {file_path}")
        
        print("\n" + "="*60)
    
    def run(self) -> bool:
        """Run the complete bootstrap process"""
        print("="*60)
        print("TPLink Deco Poller Bootstrap")
        print("="*60)
        print(f"Repository: {GITHUB_REPO}")
        print(f"Branch: {GITHUB_BRANCH}")
        print("="*60)
        
        steps = [
            ("Check privileges", self.check_privileges),
            ("Check internet connection", self.check_internet_connection),
            ("Update packages", self.update_packages),
            ("Install system dependencies", self.install_system_dependencies),
            ("Create directories", self.create_directories),
            ("Download files from GitHub", self.download_files),
            ("Setup virtual environment", self.setup_virtual_environment),
            ("Create environment file", self.create_env_file),
            ("Set permissions", self.set_permissions),
            ("Setup cron job", self.setup_cron),
        ]
        
        for step_name, step_func in steps:
            log_info(f"Step: {step_name}")
            if not step_func():
                log_error(f"Bootstrap failed at step: {step_name}")
                return False
            print()  # Add spacing between steps
        
        # Optional credential configuration
        try:
            response = input("Would you like to configure router credentials now? (Y/n): ").strip().lower()
            if response not in ('n', 'no'):
                self.configure_credentials()
        except KeyboardInterrupt:
            print("\nSkipping credential configuration")
        
        print()
        
        # Optional initial run
        try:
            response = input("Would you like to run the hosts generation now? (Y/n): ").strip().lower()
            if response not in ('n', 'no'):
                self.run_initial_generation()
        except KeyboardInterrupt:
            print("\nSkipping initial generation")
        
        self.show_summary()
        return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return
    
    print("TPLink Deco Poller Bootstrap Script")
    print("This will download and set up everything automatically.")
    print()
    
    # Show repository info
    print("Configuration:")
    print(f"  GitHub Repository: {GITHUB_REPO}")
    print(f"  Branch: {GITHUB_BRANCH}")
    print()
    
    if GITHUB_REPO == "your-username/tplink-deco-poller":
        log_error("Please update GITHUB_REPO in this script before running!")
        log_error("Edit the GITHUB_REPO variable at the top of this file.")
        sys.exit(1)
    
    bootstrap = TPLinkBootstrap()
    success = bootstrap.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
