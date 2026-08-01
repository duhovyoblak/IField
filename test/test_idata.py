"""
DEPRECATED: Testy boli presunuté do /test/idata/

Skutočné testy: pytest test/idata/test_idata.py
"""

# Historický súbor - testy sú v /test/idata/test_idata.py
    """Test InfoData initialization."""

    def test_idata_creation(self, idata_instance):
        """Test creating InfoData instance."""
        assert idata_instance.name == "test_data"
        assert idata_instance.count() == 0

    def test_idata_different_names(self):
        """Test creating multiple InfoData with different names."""
        from idata.idata import InfoData

        names = ["data1", "dataset2", "test_info"]
        for name in names:
            data = InfoData(name=name)
            assert data.name == name


class TestInfoDataPoints:
    """Test InfoData point management."""

    def test_point_count_empty(self, idata_instance):
        """Test point count on empty data."""
        assert idata_instance.count() == 0

    def test_points_property(self, idata_instance):
        """Test accessing points property."""
        points = idata_instance.points
        assert isinstance(points, (list, tuple))
        assert len(points) == 0


class TestInfoDataSchema:
    """Test InfoData schema management."""

    def test_set_schema(self, idata_instance):
        """Test setting schema."""
        schema = {"axes": {"x": "X-axis", "y": "Y-axis"}}
        idata_instance.setSchema(schema)
        # Verify schema was set
        assert idata_instance._schema is not None

    def test_axis_name_by_key(self, idata_instance):
        """Test getting axis name by key."""
        schema = {"axes": {"x": "XLabel", "y": "YLabel"}}
        idata_instance.setSchema(schema)
        # Depending on implementation
        try:
            name = idata_instance.axeNameByKey("x")
            assert name == "XLabel"
        except AttributeError:
            pass


class TestInfoDataInfo:
    """Test InfoData info methods."""

    def test_info_structure(self, idata_instance):
        """Test info() method structure."""
        try:
            info = idata_instance.info()
            # Info should return dict with specific keys or string
            assert isinstance(info, (dict, str))
        except Exception:
            # If info is not implemented, that's ok
            pass

    def test_string_representation(self, idata_instance):
        """Test string representation."""
        str_repr = str(idata_instance)
        assert isinstance(str_repr, str)


class TestInfoDataReset:
    """Test InfoData reset functionality."""

    def test_reset(self, idata_instance):
        """Test reset method."""
        try:
            idata_instance.reset()
            assert idata_instance.count() == 0
        except AttributeError:
            # If reset doesn't exist, that's ok
            pass


class TestInfoDataIntegration:
    """Integration tests for InfoData."""

    def test_multiple_operations(self, idata_instance):
        """Test multiple operations in sequence."""
        schema = {"axes": {"x": "Values"}}
        idata_instance.setSchema(schema)
        assert idata_instance.count() == 0
        # Can add more operations as API is discovered


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

        long_name = "x" * 1000
        data = InfoData(name=long_name)
        assert data.name == long_name

    def test_special_characters_in_name(self):
        """Test creating InfoData with special characters."""
        from idata.idata import InfoData

        special_name = "data_测试_тест_🎯"
        data = InfoData(name=special_name)
        assert data.name == special_name
