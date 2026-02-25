#!/usr/bin/env python3
"""
Clean patch for all ClawPersona skills - Feishu media support
"""
import os
import re

SKILLS_DIR = "/root/.openclaw/workspace/ClawPersona/skills"

# New send logic - clean and simple
NEW_LOGIC = '''        # Send or output media
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
        try:
            from feishu_media import is_feishu_env, send_media_to_feishu
            
            if args.to and (args.to.startswith("+") or args.to.isdigit()):
                # iMessage
                import subprocess
                r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
                print(f"sent: {out_path}" if r.returncode == 0 else f"MEDIA: {out_path}")
            elif is_feishu_env():
                # Feishu - send directly
                success = send_media_to_feishu(out_path)
                print(f"[已发送到飞书]" if success else f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")
        except Exception:
            print(f"MEDIA: {out_path}")'''

def clean_and_patch_skill(skill_name):
    """Clean and patch a skill's generate.py"""
    script_path = os.path.join(SKILLS_DIR, skill_name, "scripts", "generate.py")
    
    if not os.path.exists(script_path):
        return
    
    with open(script_path, "r") as f:
        content = f.read()
    
    # Find the main try block and replace everything after urllib.request.urlretrieve
    # Look for the pattern where we get out_path and then handle sending
    
    # Find: out_path = os.path.join(OUT_DIR, args.filename)
    #       urllib.request.urlretrieve(...)
    #       [REPLACE EVERYTHING AFTER THIS UNTIL except Exception]
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    in_send_block = False
    
    while i < len(lines):
        line = lines[i]
        
        # Find the line with urllib.request.urlretrieve
        if 'urllib.request.urlretrieve' in line:
            new_lines.append(line)
            # Skip everything until we find "except Exception" or similar
            i += 1
            # Skip all lines until we find the exception handler
            while i < len(lines):
                if lines[i].strip().startswith('except') or lines[i].strip().startswith('finally'):
                    break
                i += 1
            # Add our new logic
            new_lines.append('        ' + NEW_LOGIC.replace('\n', '\n        '))
            # Continue with the exception handler
            continue
        
        new_lines.append(line)
        i += 1
    
    with open(script_path, "w") as f:
        f.write('\n'.join(new_lines))
    
    print(f"Patched: {skill_name}")

def main():
    skills = [d for d in os.listdir(SKILLS_DIR) if d.startswith("clawpersona-")]
    
    for skill in sorted(skills):
        clean_and_patch_skill(skill)
    
    print("Done!")

if __name__ == "__main__":
    main()
