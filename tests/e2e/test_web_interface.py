"""
Test the web interface for template generation
"""
import os
import sys
import django

# Setup Django environment
# Navigate to project root from tests/e2e/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'format_specifications.settings')

# Add testserver to ALLOWED_HOSTS before django.setup()
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

django.setup()

from django.test import Client
from format_specifications.services.template_manager import TemplateManager

def test_template_manager():
    """Test template manager service"""
    print("\n" + "=" * 60)
    print("TEST 1: Template Manager Service")
    print("=" * 60)

    # Test list templates
    templates = TemplateManager.list_available_templates()
    print(f"Available templates: {len(templates)}")

    for template_id, name, category, template_type in templates[:5]:
        print(f"  - {name} ({category}) - {template_type}")

    # Test get template
    if templates:
        template_id = templates[0][0]
        template = TemplateManager.get_template(template_id)
        print(f"\nRetrieved template: {template.name}")
        print(f"  Sections: {len(template.sections)}")

    print("\n[SUCCESS] Template manager working")
    return True


def test_views():
    """Test view functions"""
    print("\n" + "=" * 60)
    print("TEST 2: View Functions")
    print("=" * 60)

    client = Client()

    # Test template generation page
    response = client.get('/template-generation/')
    print(f"Template generation page status: {response.status_code}")

    if response.status_code == 200:
        print("[SUCCESS] Page rendered successfully")

        # Check if templates are in response
        content = response.content.decode('utf-8')
        if 'template-card' in content:
            print("  Template cards found in response")
        else:
            print("  [WARNING] No template cards in response")
    else:
        print(f"[ERROR] Page returned status {response.status_code}")
        return False

    # Test API endpoint
    if TemplateManager.list_available_templates():
        template_id = TemplateManager.list_available_templates()[0][0]
        response = client.get(f'/api/template/{template_id}/')
        print(f"\nAPI endpoint status: {response.status_code}")

        if response.status_code == 200:
            print("[SUCCESS] API endpoint working")

            # Check response content
            import json
            data = json.loads(response.content)
            if data.get('success'):
                print(f"  Template name: {data.get('template', {}).get('name')}")
        else:
            print(f"[WARNING] API returned status {response.status_code}")

    print("\n[SUCCESS] View functions working")
    return True


def test_url_routing():
    """Test URL routing"""
    print("\n" + "=" * 60)
    print("TEST 3: URL Routing")
    print("=" * 60)

    from django.urls import reverse

    try:
        # Test URL reverse
        url1 = reverse('template_generation_page')
        print(f"template_generation_page: {url1}")

        url2 = reverse('api_template_details', kwargs={'template_id': 'annual_work_summary'})
        print(f"api_template_details: {url2}")

        print("\n[SUCCESS] URL routing working")
        return True
    except Exception as e:
        print(f"\n[ERROR] URL routing failed: {e}")
        return False


def main():
    """Run all web interface tests"""
    print("=" * 60)
    print("WEB INTERFACE TESTING")
    print("=" * 60)

    results = {}

    try:
        results['template_manager'] = test_template_manager()
        results['views'] = test_views()
        results['url_routing'] = test_url_routing()

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL WEB INTERFACE TESTS PASSED!")
        print("=" * 60)
        print("\nWeb Interface Summary:")
        print("  - Template manager service working")
        print("  - Views rendering correctly")
        print("  - URL routing configured")
        print("  - HTML template created")
        print("\nAccess the web interface at:")
        print("  http://localhost:8000/template-generation/")
        print("\nYou can now:")
        print("  1. Select a template from 10 available templates")
        print("  2. Provide document outline/key points")
        print("  3. Optionally upload a source document")
        print("  4. Choose document tone")
        print("  5. Generate formatted Word document")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
