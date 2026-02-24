#!/usr/bin/env python3
"""
Patch all ClawPersona skills to use unified Feishu media sender
"""
import os

SKILLS_DIR = "/root/.openclaw/workspace/ClawPersona/skills"

NEW_SEND_LOGIC = '''        # Send or output media
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
        try:
            from feishu_media import handle_media_output, is_feishu_env, send_media_to_feishu
            
            if args.to:
                # Explicit recipient specified
                import subprocess
                if args.to.startswith("+") or args.to.isdigit():
                    # iMessage
                    r = subprocess.run(["imsg", "send", "--to", args.to, "--file", out_path, "--service", "imessage"], capture_output=True)
                    if r.returncode != 0:
                        print(f"MEDIA: {out_path}")
                    else:
                        print(f"sent: {out_path}")
                else:
                    # Try to send directly
                    print(handle_media_output(out_path, args.to))
            elif is_feishu_env():
                # In Feishu environment - send directly
                success = send_media_to_feishu(out_path)
                if success:
                    print(f"[已发送到飞书]")
                else:
                    print(f"MEDIA: {out_path}")
            else:
                # Default output
                print(f"MEDIA: {out_path}")
        except ImportError as e:
            print(f"Warning: Feishu media sender not available: {e}", file=sys.stderr)
            print(f"MEDIA: {out_path}")'''

def patch_skill(skill_name):
    """Patch a single skill's generate.py"""
    script_path = os.path.join(SKILLS_DIR, skill_name, "scripts", "generate.py")
    
    if not os.path.exists(script_path):
        print(f"Skip: {skill_name}")
        return
    
    with open(script_path, "r") as f:
        content = f.read()
    
    # Check if already patched
    if "feishu_media" in content:
        print(f"Already patched: {skill_name}")
        return
    
    # Find and replace the send logic
    # Look for the pattern that handles args.to and OPENCLAW_CHANNEL
    if "if args.to:" in content and "OPENCLAW_CHANNEL" in content:
        # Find the start of the send logic
        import re
        
        # Pattern to match the entire send block
        pattern = r'(if args\.to:.*?print\(f"MEDIA: \{out_path\}"\))'
        
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_content = content[:match.start()] + NEW_SEND_LOGIC + content[match.end():]
            with open(script_path, "w") as f:
                f.write(new_content)
            print(f"Patched: {skill_name}")
            return
    
    print(f"Pattern not found: {skill_name}")

def main():
    skills = [d for d in os.listdir(SKILLS_DIR) if d.startswith("clawpersona-")]
    
    print(f"Found {len(skills)} skills")
    print("-" * 40)
    
    for skill in sorted(skills):
        patch_skill(skill)
    
    print("-" * 40)
    print("Done!")

if __name__ == "__main__":
    main()
