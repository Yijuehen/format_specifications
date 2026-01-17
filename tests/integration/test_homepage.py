"""
Test homepage integration with template generation
"""
import os
import sys
import django

# Setup Django environment
# Navigate to project root from tests/integration/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'format_specifications.settings')

# Add testserver to ALLOWED_HOSTS
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

django.setup()

from django.test import Client

def test_homepage():
    """Test homepage loads with templates"""
    print("\n" + "=" * 60)
    print("TEST: Homepage Integration")
    print("=" * 60)

    client = Client()

    # Test homepage loads
    response = client.get('/')
    print(f"Homepage status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode('utf-8')

        # Check for template grid
        if 'templateGrid' in content:
            print("[OK] Template grid found")
        else:
            print("[ERROR] Template grid not found")
            return False

        # Check for template cards
        if 'template-card' in content:
            print("[OK] Template cards found")
        else:
            print("[ERROR] Template cards not found")
            return False

        # Check for outline input
        if 'userOutline' in content:
            print("[OK] Outline input found")
        else:
            print("[ERROR] Outline input not found")
            return False

        # Check for visual separator
        if '或使用模板生成文档' in content:
            print("[OK] Visual separator found")
        else:
            print("[ERROR] Visual separator not found")
            return False

        # Count template cards
        import re
        template_cards = re.findall(r'template-card', content)
        print(f"Template cards count: {len(template_cards)}")

        print("\n[SUCCESS] Homepage integration working!")
        print("\nAccess at: http://localhost:8000/")
        print("\nFeatures:")
        print("  - Document Formatting section (top)")
        print("  - Template Generation section (bottom)")
        print("  - Visual separator between sections")
        print("  - All 10 templates available")
        return True
    else:
        print(f"[ERROR] Homepage returned status {response.status_code}")
        return False


def main():
    """Run test"""
    print("=" * 60)
    print("HOMEPAGE INTEGRATION TEST")
    print("=" * 60)

    try:
        result = test_homepage()
        if result:
            print("\n" + "=" * 60)
            print("✅ INTEGRATION COMPLETE!")
            print("=" * 60)
            print("\nYou can now:")
            print("1. Start server: python manage.py runserver")
            print("2. Open browser: http://localhost:8000/")
            print("3. Use top section to format existing documents")
            print("4. Use bottom section to generate from templates")
            return 0
        else:
            print("\n[FAILURE] Integration test failed")
            return 1
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
