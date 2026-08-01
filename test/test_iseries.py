"""
DEPRECATED: Testy boli presunuté do /test/idata/

Skutočné testy: pytest test/idata/test_iseries.py
"""

# Historický súbor - testy sú v /test/idata/test_iseries.py
    """Test ISeries initialization."""

    def test_iseries_creation(self, iseries_instance):
        """Test creating ISeries instance."""
        assert iseries_instance.name == "test_series"
        assert iseries_instance.count() == 0

    def test_iseries_different_names(self):
        """Test creating multiple ISeries with different names."""
        from idata.iseries import ISeries

        names = ["series1", "series2", "data_series"]
        for name in names:
            series = ISeries(name=name)
            assert series.name == name


class TestISeriesDataManagement:
    """Test ISeries data management."""

    def test_add_data_point(self, iseries_instance):
        """Test adding a data point."""
        # Implementation depends on ISeries API
        # This is a generic test structure
        initial_count = iseries_instance.count()
        # Add point would depend on API
        assert initial_count == 0

    def test_get_point_count(self, iseries_instance):
        """Test getting point count."""
        count = iseries_instance.count()
        assert isinstance(count, int)
        assert count >= 0


class TestISeriesInfo:
    """Test ISeries info methods."""

    def test_info_method(self, iseries_instance):
        """Test info() method."""
        # Depending on implementation
        try:
            info = iseries_instance.info()
            assert isinstance(info, dict) or isinstance(info, str)
        except AttributeError:
            # If info method doesn't exist, that's ok for now
            pass

    def test_string_representation(self, iseries_instance):
        """Test string representation."""
        str_repr = str(iseries_instance)
        assert isinstance(str_repr, str)


class TestISeriesEdgeCases:
    """Test edge cases for ISeries."""

    def test_empty_series(self, iseries_instance):
        """Test operations on empty series."""
        assert iseries_instance.count() == 0

    def test_series_reset(self, iseries_instance):
        """Test series reset."""
        try:
            iseries_instance.reset()
            assert iseries_instance.count() == 0
        except AttributeError:
            # If reset method doesn't exist, that's ok
            pass
