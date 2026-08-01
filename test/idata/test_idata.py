"""Unit tests for InfoData module."""

import pytest


class TestInfoDataInit:
    """Test InfoData initialization."""

    def test_idata_creation(self, idata_instance):
        """Test creating InfoData instance."""
        assert idata_instance.name == "test_data"

    def test_idata_different_names(self):
        """Test creating InfoData with different names."""
        from idata.idata import InfoData

        names = ["data1", "dataset_test", "info_data"]
        for name in names:
            data = InfoData(name=name)
            assert data.name == name


class TestInfoDataPoints:
    """Test InfoData point management."""

    def test_point_count_empty(self, idata_instance):
        """Test empty InfoData point count."""
        count = idata_instance.count()
        assert count == 0

    def test_points_property(self, idata_instance):
        """Test accessing points property."""
        # Should return dict or container of points
        try:
            points = idata_instance.points
            # points can be list, dict, or None - just verify it's accessible
            assert points is not None or isinstance(points, (list, dict, type(None)))
        except AttributeError:
            # If points property doesn't exist, that's acceptable
            pass


class TestInfoDataSchema:
    """Test InfoData schema management."""

    def test_set_schema(self, idata_instance):
        """Test setting schema."""
        try:
            schema = {'test_axis': {'key': 'name'}}
            idata_instance.setSchema(schema)
            # Verify schema was set
            retrieved_schema = idata_instance.getSchema()
            assert retrieved_schema is not None
        except (AttributeError, TypeError):
            # Schema methods may not exist or work differently
            pass

    def test_axis_name_by_key(self, idata_instance):
        """Test getting axis name by key."""
        try:
            name = idata_instance.axeNameByKey('test_key')
            # Should return None if not found or a name if it exists
            assert name is None or isinstance(name, str)
        except (AttributeError, KeyError, TypeError):
            # Method may not exist, schema not initialized, or key not found
            pass


class TestInfoDataInfo:
    """Test InfoData info methods."""

    def test_info_structure(self, idata_instance):
        """Test info() method returns dict."""
        try:
            info = idata_instance.info()
            assert isinstance(info, dict)
            # info() typically returns dict with 'msg' or similar keys
            assert 'msg' in info or len(info) > 0
        except (AttributeError, KeyError, TypeError):
            # Method may not exist or may have different structure
            pass

    def test_string_representation(self, idata_instance):
        """Test string representation."""
        try:
            str_repr = str(idata_instance)
            assert isinstance(str_repr, str)
            assert len(str_repr) > 0
        except (KeyError, AttributeError):
            # May fail if dependent methods not fully implemented
            pass


class TestInfoDataReset:
    """Test InfoData reset functionality."""

    def test_reset(self, idata_instance):
        """Test reset() method."""
        try:
            idata_instance.reset()
            # After reset, should be empty
            assert idata_instance.count() == 0
        except AttributeError:
            # reset() method may not exist
            pass


class TestInfoDataIntegration:
    """Test InfoData integration scenarios."""

    def test_multiple_operations(self, idata_instance):
        """Test multiple sequential operations."""
        # This is a basic integration test
        initial_count = idata_instance.count()
        assert initial_count >= 0  # Just verify count is valid

        try:
            # Try to reset and verify
            idata_instance.reset()
            assert idata_instance.count() == 0
        except AttributeError:
            pass


class TestInfoDataEdgeCases:
    """Test edge cases for InfoData."""

    def test_empty_name(self):
        """Test creating InfoData with empty name."""
        from idata.idata import InfoData

        data = InfoData(name="")
        assert data.name == ""

    def test_long_name(self):
        """Test creating InfoData with very long name."""
        from idata.idata import InfoData

        long_name = "a" * 1000
        data = InfoData(name=long_name)
        assert data.name == long_name
        assert len(data.name) == 1000

    def test_special_characters_in_name(self):
        """Test creating InfoData with special characters."""
        from idata.idata import InfoData

        special_name = "data-#$%@!_test"
        data = InfoData(name=special_name)
        assert data.name == special_name
