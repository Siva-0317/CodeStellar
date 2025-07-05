import os
import subprocess

# Paths
input_dem = "data/raw/strm_30m_chennai.tif"
output_dir = "data/processed"
whitebox_exe = r"C:\Users\USER\Downloads\WhiteboxTools_win_amd64\WBT\whitebox_tools.exe"
  # Update if different

# Derived files
slope = os.path.join(output_dir, "slope.tif")
aspect = os.path.join(output_dir, "aspect.tif")
hillshade = os.path.join(output_dir, "hillshade.tif")

# Commands
commands = [
    f'"{whitebox_exe}" --run="Slope" --dem="{input_dem}" --output="{slope}" --units="degrees"',
    f'"{whitebox_exe}" --run="Aspect" --dem="{input_dem}" --output="{aspect}"',
    f'"{whitebox_exe}" --run="Hillshade" --dem="{input_dem}" --output="{hillshade}"'
]

# Run commands
for cmd in commands:
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)
