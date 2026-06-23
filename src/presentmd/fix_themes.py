import os
import glob
import re

THEMES_DIR = "/home/jaime/programacion/PresentMD/src/presentmd/templates/themes"
files = glob.glob(os.path.join(THEMES_DIR, "**", "styles.css"), recursive=True)

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Task 1: remove duplicate slide-counter sizes
    # Remove: .slide-counter { font-size: 11px !important; }
    # Or similar
    content = re.sub(r'\.slide-counter\s*\{\s*font-size:\s*11px\s*!important;\s*\}', '', content)
    # also remove for toc-sidebar if it has a duplicate, wait, the audit only mentioned .slide-counter, but I'll remove it. Let's just do slide-counter as requested.
    
    # Task 2: fix bar-label positioning
    # .bar-chart-column needs `overflow: visible; position: relative;`
    # Replace:
    # .bar-chart-column {
    #   display: flex;
    #   flex-direction: column;
    #   align-items: center;
    #   justify-content: flex-end;
    #   height: 100%;
    #   transition: opacity 0.5s ease, transform 0.5s ease;
    #   transition-delay: calc(var(--step-idx) * 0.1s);
    # }
    
    content = re.sub(
        r'(\.bar-chart-column\s*\{[^\}]*?transition-delay:\s*calc[^\}]*?;)(\n\})',
        r'\1\n  overflow: visible;\n  position: relative;\2',
        content
    )
    
    # Replace:
    # .bar-label {
    #   font-size: 14px;
    #   font-weight: 600;
    #   color: var(--text-muted, #64748b);
    #   margin-top: 12px;
    #   position: absolute;
    #   bottom: -30px;
    # }
    content = re.sub(
        r'(\.bar-label\s*\{[^\}]*?margin-top:\s*12px;)\s*position:\s*absolute;\s*bottom:\s*-30px;\s*(\})',
        r'\1\2',
        content
    )
    
    # Special fix for swiss grid line 779
    if "swiss-grid" in file:
        content = re.sub(
            r'(\.slide\s*\{[^}]*?position:\s*relative\s*!important;\s*)border:\s*4px\s*solid\s*var\(--border-color\)\s*!important;([^}]*?\})',
            r'\1border: none !important;\n    box-shadow: inset 0 0 0 4px var(--border-color) !important;\2',
            content
        )
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Themes fixed.")
