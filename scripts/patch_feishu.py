#!/usr/bin/env python3
"""Patch all ClawPersona skills to support Feishu."""
import os
import re

SKILLS_DIR = "/root/.openclaw/workspace/ClawPersona/skills"

# The new send logic to inject
FEISHU_LOGIC = '''
        if args.to:
            import subprocess
            # Check if it's a phone number (iMessage) or other format
            if args.to.startswith("+") or args.to.isdigit():
                r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
                if r.returncode != 0:
                    print(f"MEDIA: {out_path}")
                else:
                    print(f"sent: {out_path}")
            elif args.to.startswith("feishu:"):
                # Feishu webhook URL
                webhook_url = args.to[7:]  # Remove "feishu:" prefix
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../scripts"))
                try:
                    from feishu_sender import send_to_feishu
                    send_to_feishu(out_path, None, webhook_url)
                except ImportError:
                    print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")
        else:
            # Check if running in Feishu environment
            if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../scripts"))
                try:
                    from feishu_adapter import adapt_for_feishu
                    print(adapt_for_feishu(out_path))
                except ImportError:
                    print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")'''

OLD_PATTERN = r'''        if args\.to:\s*
            import subprocess\s*
            r = subprocess\.run\(\["imsg", "send", "--to", args\.to, "--file", out_path, "--service", "imessage"\], capture_output=True\)\s*
            if r\.returncode != 0:\s*
                print\(f"MEDIA: \{out_path\}"\)\s*
            else:\s*
                print\(f"sent: \{out_path\}"\)\s*
        else:\s*
            print\(f"MEDIA: \{out_path\}"\)'''

def patch_skill(skill_name):
    """Patch a single skill's generate.py."""
    script_path = os.path.join(SKILLS_DIR, skill_name, "scripts", "generate.py")
    
    if not os.path.exists(script_path):
        print(f"Skip: {skill_name} (no generate.py)")
        return
    
    with open(script_path, "r") as f:
        content = f.read()
    
    # Check if already patched
    if "feishu:" in content or "feishu_adapter" in content:
        print(f"Skip: {skill_name} (already patched)")
        return
    
    # Replace the send logic
    new_content = re.sub(OLD_PATTERN, FEISHU_LOGIC, content, flags=re.MULTILINE)
    
    if new_content == content:
        # Pattern didn't match, try simpler replacement
        old_simple = '''        if args.to:
            import subprocess
            r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
            if r.returncode != 0:
                print(f"MEDIA: {out_path}")
            else:
                print(f"sent: {out_path}")
        else:
            print(f"MEDIA: {out_path}")'''
        
        if old_simple in content:
            new_content = content.replace(old_simple, FEISHU_LOGIC)
        else:
            print(f"Warning: {skill_name} pattern not matched")
            return
    
    with open(script_path, "w") as f:
        f.write(new_content)
    
    print(f"Patched: {skill_name}")

def main():
    """Patch all skills."""
    skills = [d for d in os.listdir(SKILLS_DIR) if d.startswith("clawpersona-")]
    
    print(f"Found {len(skills)} skills to patch")
    print("-" * 40)
    
    for skill in sorted(skills):
        patch_skill(skill)
    
    print("-" * 40)
    print("Done!")

if __name__ == "__main__":
    main()
