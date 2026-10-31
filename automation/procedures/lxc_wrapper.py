import subprocess
import sys

def run_lxc_command(args):
    """
    Executes an LXC command. If direct execution fails due to socket 
    inaccessibility (common in Termux/Host), it bridges the command 
    via 'vsh termina'.
    """
    # Try direct lxc call first
    cmd_direct = ["lxc"] + args
    try:
        result = subprocess.run(
            cmd_direct, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Check if failure is due to socket/connection (typical for host-to-VM)
        error_msg = getattr(e, 'stderr', str(e)).lower()
        if "socket" in error_msg or "connection refused" in error_msg or "not found" in error_msg:
            # Fallback: Bridge via vsh termina
            cmd_bridge = ["vsh", "termina", "--", "lxc"] + args
            try:
                result = subprocess.run(
                    cmd_bridge, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as be:
                print(f"[ERROR] Bridge failed: {be.stderr}", file=sys.stderr)
                raise be
        else:
            # It was a genuine LXC error (e.g., container not found), re-raise it
            raise e

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            print(run_lxc_command(sys.argv[1:]))
        except Exception as e:
            print(f"Error: {e}")
