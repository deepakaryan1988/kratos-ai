import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from agents.scanner import cloud_scanner_node

def test_scanner_returns_findings():
    result = cloud_scanner_node({"findings": [], "status": "test"})
    assert "findings" in result
    assert isinstance(result["findings"], list)
    assert "status" in result

def test_scanner_handles_no_buckets():
    result = cloud_scanner_node({"findings": [], "status": "test"})
    assert result["status"] == "Scanning Complete"