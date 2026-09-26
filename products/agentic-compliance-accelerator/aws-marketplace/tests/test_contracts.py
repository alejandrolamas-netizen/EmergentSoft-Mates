from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_marketplace_package_has_required_documents():
    required = [
        "README.md",
        "marketplace/listing.md",
        "marketplace/pricing.md",
        "marketplace/submission-checklist.md",
        "marketplace/field-map.md",
        "architecture/saas-architecture.md",
        "legal/compliance-disclaimer.md",
        "onboarding/customer-onboarding.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_fulfillment_service_has_runtime_contract():
    service = ROOT / "services" / "fulfillment"
    assert (service / "app.py").exists()
    assert (service / "requirements.txt").exists()
    assert (service / "Dockerfile").exists()
