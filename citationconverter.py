# coding=utf-8
import re

# Read your LaTeX file
with open("C:/Users/jmayhall\Downloads/tke_outflow_outline/amspaperV6.1.tex", "r", encoding="utf-8") as f:
    tex_content = f.read()

# Regex pattern to match \citeauthor{key} \citeyear{key}
pattern = re.compile(r"\\citeauthor\{(\w+)\}\s+\\citeyear\{\1\}")

# Replace with \citet{key}
new_tex_content = pattern.sub(r"\\citet{\1}", tex_content)

# Save to a new file
with open("C:/Users/jmayhall\Downloads/tke_outflow_outline/amspaperV6.1_new.tex", "w", encoding="utf-8") as f:
    f.write(new_tex_content)
