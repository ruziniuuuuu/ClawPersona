#!/usr/bin/env python3
"""Update all skills to use feishu_direct.py for sending images."""
import os
import re

SKILLS_DIR = "/root/.openclaw/workspace/ClawPersona/skills"

OLD_CODE = '''        else:
            # Check if running in Feishu environment
            if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
                try:
                    from feishu_adapter import adapt_for_feishu
                    print(adapt_for_feishu(out_path))
                except ImportError:
                    print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")'''

NEW_CODE = '''        else:
            # Check if running in Feishu environment
            if os.environ.get("OPENCLAW_CHANNEL") == "feishu":
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../workspace/ClawPersona/scripts"))
                try:
                    from feishu_direct import send_image_to_feishu
                    success = send_image_to_feishu(out_path)
                    if not success:
                        # Fallback to adapter
                        from feishu_adapter import adapt_for_feishu
                        print(adapt_for_feishu(out_path))
                except ImportError:
                    # Fallback to adapter
                    try:
                        from feishu_adapter import adapt_for_feishu
                        print(adapt_for_feishu(out_path))
                    except ImportError:
                        print(f"MEDIA: {out_path}")
            else:
                print(f"MEDIA: {out_path}")'''

def update_skill(skill_name):
    """Update a single skill's generate.py."""
    script_path = os.path.join(SKILLS_DIR, skill_name, "scripts", "generate.py")
    
    if not os.path.exists(script_path):
        print(f"Skip: {skill_name} (no generate.py)")
        return
    
    with open(script_path, "r") as f:
        content = f.read()
    
    if "feishu_direct" in content:
        print(f"Skip: {skill_name} (already updated)")
        return
    
    if OLD_CODE in content:
        new_content = content.replace(OLD_CODE, NEW_CODE)
        with open(script_path, "w") as f:
            f.write(new_content)
        print(f"Updated: {skill_name}")
    else:
        print(f"Warning: {skill_name} - pattern not found")

def main():
    skills = [d for d in os.listdir(SKILLS_DIR) if d.startswith("clawpersona-")]
    
    print(f"Found {len(skills)} skills to update")
    print("-" * 40)
    
    for skill in sorted(skills):
        update_skill(skill)
    
    print("-" * 40)
    print("Done!")

if __name__ == "__main__":
    main()
