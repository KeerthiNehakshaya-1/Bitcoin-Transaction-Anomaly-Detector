from ml.risk_scoring import (
    assign_risk_level,
    calculate_confidence
)


def test_risk_levels():

    assert assign_risk_level(90) == "CRITICAL"
    assert assign_risk_level(70) == "HIGH"
    assert assign_risk_level(50) == "MEDIUM"
    assert assign_risk_level(20) == "LOW"


def test_confidence_range():

    confidence = calculate_confidence(90)

    assert 0 <= confidence <= 0.99