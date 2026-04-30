import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from vault.policy_store import get_embedding

def test_embedding_returns_list():
    result = get_embedding("test finding")
    assert isinstance(result, list)
    assert len(result) == 768