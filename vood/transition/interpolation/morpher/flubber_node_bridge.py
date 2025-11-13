"""
Bridge to Flubber JavaScript library for advanced path morphing
"""

import subprocess
import json
import os


class FlubberNodeBridge:
    """
    Persistent Flubber interpolator that keeps Node.js process alive.
    Call it repeatedly with different t values efficiently.
    """

    def __init__(self, shape1, shape2, flubber_path=None, node_modules_path=None):
        """
        Create interpolator between two shapes.

        Args:
            shape1: SVG path string
            shape2: SVG path string
            flubber_path: Path to flubber installation directory (optional)
            node_modules_path: Direct path to node_modules folder (optional)
        """
        self.shape1 = shape1
        self.shape2 = shape2
        self.flubber_path = flubber_path
        self.node_modules_path = node_modules_path
        self.process = None
        self._start_process()

    def _find_node_modules(self):
        """Find node_modules directory"""
        if self.node_modules_path:
            if not os.path.isdir(self.node_modules_path):
                raise FileNotFoundError(
                    f"Specified node_modules path does not exist: {self.node_modules_path}"
                )
            flubber_module = os.path.join(self.node_modules_path, "flubber")
            if not os.path.isdir(flubber_module):
                raise FileNotFoundError(
                    f"Flubber not found in: {self.node_modules_path}\n"
                    f"Install it with: cd {os.path.dirname(self.node_modules_path)} && npm install flubber"
                )
            return self.node_modules_path

        search_paths = []

        if self.flubber_path:
            if not os.path.isdir(self.flubber_path):
                raise FileNotFoundError(
                    f"Specified flubber_path does not exist: {self.flubber_path}"
                )
            search_paths.append(self.flubber_path)

        # Add current directory and up to 5 parent directories
        current = os.getcwd()
        for _ in range(6):
            search_paths.append(current)
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

        # Check each path for node_modules
        for path in search_paths:
            node_modules = os.path.join(path, "node_modules")
            flubber_module = os.path.join(node_modules, "flubber")
            if os.path.isdir(flubber_module):
                return node_modules

        return None

    def _start_process(self):
        """Start persistent Node.js process"""
        script = """
        const flubber = require('flubber');
        const readline = require('readline');
        
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        let interpolator = null;
        
        rl.on('line', (line) => {
            try {
                const msg = JSON.parse(line);
                
                if (msg.command === 'setup') {
                    interpolator = flubber.interpolate(msg.shape1, msg.shape2,{ maxSegmentLength: 0.5 } );
                    console.log(JSON.stringify({status: 'ready'}));
                } 
                else if (msg.command === 'interpolate') {
                    if (!interpolator) {
                        console.log(JSON.stringify({error: 'Not initialized'}));
                    } else {
                        const result = interpolator(msg.t);
                        console.log(JSON.stringify({result: result}));
                    }
                }
                else if (msg.command === 'exit') {
                    process.exit(0);
                }
            } catch (e) {
                console.log(JSON.stringify({error: e.message}));
            }
        });
        """

        # Prepare environment
        env = os.environ.copy()
        node_modules = None

        try:
            node_modules = self._find_node_modules()
        except FileNotFoundError as e:
            raise RuntimeError(str(e)) from e

        if node_modules:
            node_path = env.get("NODE_PATH", "")
            if node_path:
                env["NODE_PATH"] = f"{node_modules}{os.pathsep}{node_path}"
            else:
                env["NODE_PATH"] = node_modules

        try:
            self.process = subprocess.Popen(
                ["node", "-e", script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
                cwd=self.flubber_path if self.flubber_path else None,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Node.js not found!\n"
                "Please install Node.js from: https://nodejs.org/\n"
                "Or install via package manager:\n"
                "  - Mac: brew install node\n"
                "  - Ubuntu/Debian: sudo apt install nodejs npm\n"
                "  - Windows: Download from nodejs.org"
            )

        # Setup interpolator
        self._send_command(
            {"command": "setup", "shape1": self.shape1, "shape2": self.shape2}
        )

        try:
            response = self._read_response()
        except json.JSONDecodeError:
            stderr_output = self.process.stderr.read()

            if "Cannot find module 'flubber'" in stderr_output:
                search_info = [f"  - Current directory: {os.getcwd()}/node_modules"]
                if self.node_modules_path:
                    search_info.insert(
                        0, f"  - Specified path: {self.node_modules_path}"
                    )
                elif self.flubber_path:
                    search_info.insert(
                        0, f"  - Specified path: {self.flubber_path}/node_modules"
                    )
                search_info.append(f"  - Global npm modules")

                raise RuntimeError(
                    "Flubber JavaScript library not found!\n\n"
                    "Searched in:\n" + "\n".join(search_info) + "\n\n"
                    "To fix this, install Flubber:\n\n"
                    "Option 1 - Install locally (recommended):\n"
                    f"  cd {os.getcwd()}\n"
                    "  npm install flubber\n\n"
                    "Option 2 - Install globally:\n"
                    "  npm install -g flubber\n\n"
                    "Option 3 - Specify custom path:\n"
                    "  FlubberMorpher(shape1, shape2, flubber_path='/your/path')"
                )
            else:
                raise RuntimeError(
                    f"Failed to initialize Flubber.\n"
                    f"Node.js error:\n{stderr_output}"
                )

        if response.get("status") != "ready":
            error_msg = (
                self.process.stderr.read() if self.process.stderr else "Unknown error"
            )
            raise RuntimeError(
                f"Failed to initialize Flubber interpolator.\n"
                f"Response: {response}\n"
                f"Error output: {error_msg}"
            )

    def _send_command(self, cmd):
        """Send command to Node.js process"""
        self.process.stdin.write(json.dumps(cmd) + "\n")
        self.process.stdin.flush()

    def _read_response(self):
        """Read response from Node.js process"""
        line = self.process.stdout.readline()
        return json.loads(line)

    def interpolate(self, t):
        """
        Get interpolated shape at t value.

        Args:
            t: Float between 0.0 and 1.0

        Returns:
            SVG path string
        """

        self._send_command({"command": "interpolate", "t": t})
        response = self._read_response()

        if "error" in response:
            raise RuntimeError(f"Interpolation error: {response['error']}")

        return response["result"]

    def close(self):
        """Close the Node.js process"""
        if self.process:
            try:
                self._send_command({"command": "exit"})
                self.process.wait(timeout=1)
            except:
                self.process.kill()
            finally:
                self.process = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
