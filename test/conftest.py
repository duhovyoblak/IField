"""Pytest configuration and fixtures for IField tests."""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, src_path)

import pytest


@pytest.fixture
def idata_instance():
    """Create a fresh InfoData instance for testing."""
    from idata.idata import InfoData
    return InfoData(name="test_data")


@pytest.fixture
def imarkov_instance():
    """Create a fresh IMarkov instance for testing."""
    from idata.imarkov import IMarkov
    return IMarkov(name="test_markov", dim=1)


@pytest.fixture
def ipoint_instance():
    """Create a fresh InfoPoint instance for testing."""
    from idata.ipoint import InfoPoint
    return InfoPoint(pos={'x': 0})


@pytest.fixture
def iseries_instance():
    """Create a fresh ISeries instance for testing."""
    from idata.iseries import ISeries
    return ISeries(name="test_series")
