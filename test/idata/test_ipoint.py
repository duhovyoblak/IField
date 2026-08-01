"""Unit tests for IPoint module."""

import pytest


class TestIPointInit:
    """Test IPoint initialization."""

    def test_ipoint_creation_1d(self, ipoint_instance):
        """Test creating 1D InfoPoint."""
        assert ipoint_instance._pos["x"] == 0
        assert ipoint_instance.pos("x") == 0

    def test_ipoint_creation_with_different_positions(self):
        """Test creating points with different positions."""
        from idata.ipoint import InfoPoint

        positions = [0, 1, -5, 100.5]
        for pos in positions:
            point = InfoPoint(pos={"x": pos})
            assert point.pos("x") == pos

    def test_ipoint_string_representation(self, ipoint_instance):
        """Test string representation of InfoPoint."""
        str_repr = str(ipoint_instance)
        assert isinstance(str_repr, str)


class TestIPointValues:
    """Test IPoint value management."""

    def test_set_and_get_value(self, ipoint_instance):
        """Test setting and getting values."""
        ipoint_instance.set(vals={"test_key": 42})
        value = ipoint_instance.val(valKey="test_key")
        assert value == 42

    def test_set_multiple_values(self, ipoint_instance):
        """Test setting multiple values."""
        ipoint_instance.set(vals={"key1": 10, "key2": 20})
        assert ipoint_instance.val(valKey="key1") == 10
        assert ipoint_instance.val(valKey="key2") == 20

    def test_get_nonexistent_value(self, ipoint_instance):
        """Test getting non-existent value."""
        # Should return None or raise KeyError based on implementation
        try:
            value = ipoint_instance.val(valKey="nonexistent")
            assert value is None or isinstance(value, type(None))
        except KeyError:
            pass  # This is also acceptable behavior


class TestIPointComparison:
    """Test InfoPoint comparison."""

    def test_point_equality(self):
        """Test point equality comparison."""
        from idata.ipoint import InfoPoint

        p1 = InfoPoint(pos={"x": 1})
        p2 = InfoPoint(pos={"x": 1})
        # Points with same position should be comparable
        assert p1.pos("x") == p2.pos("x")

    def test_point_inequality(self):
        """Test point inequality."""
        from idata.ipoint import InfoPoint

        p1 = InfoPoint(pos={"x": 1})
        p2 = InfoPoint(pos={"x": 2})
        assert p1.pos("x") != p2.pos("x")


class TestIPointEdgeCases:
    """Test edge cases for InfoPoint."""

    def test_zero_position(self):
        """Test point at zero position."""
        from idata.ipoint import InfoPoint

        point = InfoPoint(pos={"x": 0})
        assert point.pos("x") == 0

    def test_negative_position(self):
        """Test point at negative position."""
        from idata.ipoint import InfoPoint

        point = InfoPoint(pos={"x": -100})
        assert point.pos("x") == -100

    def test_float_position(self):
        """Test point at float position."""
        from idata.ipoint import InfoPoint

        point = InfoPoint(pos={"x": 3.14159})
        assert abs(point.pos("x") - 3.14159) < 0.001
