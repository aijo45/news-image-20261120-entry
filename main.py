"""Entry program: copy the repository's entry.png to the output directory."""
import os
import shutil

out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
shutil.copyfile(src, os.path.join(out, "entry.png"))
