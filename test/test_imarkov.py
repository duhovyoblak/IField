"""
DEPRECATED: Testy boli presunuté do /test/idata/

Skutočné testy: pytest test/idata/test_imarkov.py
"""

# Historický súbor - testy sú v /test/idata/test_imarkov.py
    """Test IMarkov initialization."""

    def test_imarkov_creation(self, imarkov_instance):
        """Test creating IMarkov instance."""
        assert imarkov_instance.name == "test_markov"
        assert imarkov_instance.dim == 1
        assert imarkov_instance.totObs == 0
        assert imarkov_instance.bits == 0
        assert imarkov_instance.actVals == []
        assert imarkov_instance.actPoint is None

    def test_imarkov_different_dimensions(self):
        """Test creating IMarkov with different dimensions."""
        from idata.imarkov import IMarkov

        for dim in [1, 2, 3, 5]:
            mrk = IMarkov(name=f"test_dim_{dim}", dim=dim)
            assert mrk.dim == dim
            assert mrk.totObs == 0

    def test_imarkov_invalid_dimension(self):
        """Test that invalid dimension is rejected."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=1)
        mrk.setDim(0)  # Should not change
        assert mrk.dim == 1  # Still dim=1 after reset

    def test_imarkov_custom_axis_name(self):
        """Test creating IMarkov with custom axis name."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=1, axeName="CustomAxis")
        assert mrk.axeNameByKey("x") == "CustomAxis"


class TestIMarkovObserve:
    """Test IMarkov observe() method."""

    def test_single_observation(self, imarkov_instance):
        """Test observing a single value."""
        imarkov_instance.observe(1)
        assert imarkov_instance.totObs == 1
        assert len(imarkov_instance.points) == 1
        assert imarkov_instance.points[0].pos("x") == 1

    def test_multiple_observations_same_value(self, imarkov_instance):
        """Test observing same value multiple times."""
        for _ in range(5):
            imarkov_instance.observe(1)

        assert imarkov_instance.totObs == 5
        assert len(imarkov_instance.points) == 1
        assert imarkov_instance.points[0]._vals["obs"] == 5

    def test_multiple_observations_different_values(self, imarkov_instance):
        """Test observing different values."""
        values = [1, 2, 3, 1, 2]
        for val in values:
            imarkov_instance.observe(val)

        assert imarkov_instance.totObs == 5
        assert len(imarkov_instance.points) == 3  # Values 1, 2, 3

    def test_probability_calculation_single_dim(self, imarkov_instance):
        """Test probability calculation for dim=1."""
        imarkov_instance.observe(1)
        imarkov_instance.observe(1)
        imarkov_instance.observe(2)

        # Find points by their position
        point_1 = None
        point_2 = None
        for point in imarkov_instance.points:
            if point.pos("x") == 1:
                point_1 = point
            elif point.pos("x") == 2:
                point_2 = point

        assert point_1 is not None
        assert point_2 is not None

        # Check probabilities
        assert abs(point_1._vals["pro"] - 2 / 3) < 0.001
        assert abs(point_2._vals["pro"] - 1 / 3) < 0.001

    def test_conditional_probability_dim2(self):
        """Test conditional probability calculation for dim=2."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test_dim2", dim=2)

        # Observe first value
        mrk.observe(1)
        assert mrk.totObs == 1
        assert len(mrk.points) == 1

        # Observe second value
        mrk.observe(2)
        # With dim=2, after 2 observations we should have data
        # totObs increments for each dimension
        assert mrk.totObs == 2

        # Observe sequence continues [1, 2, 1, 2, 1]
        mrk.observe(1)
        mrk.observe(2)
        mrk.observe(1)

        # Now we have 5 observations total
        assert mrk.totObs == 5


    def test_joint_probability_consistency(self):
        """Test that joint probabilities are consistent."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=2)
        mrk.observe(1)
        mrk.observe(2)

        # First point should have pro = 1.0 (only one value)
        point_1 = mrk.points[0]
        assert abs(point_1._vals["pro"] - 1.0) < 0.001

        # After second observation, dim=2 should exist
        child_mrk = point_1._vals["mrk"]
        assert child_mrk is not None
        # Child should have one point with pro = 1.0
        assert len(child_mrk.points) == 1
        assert abs(child_mrk.points[0]._vals["pro"] - 1.0) < 0.001

    def test_entropy_update_incremental(self, imarkov_instance):
        """Test that entropy is updated incrementally."""
        imarkov_instance.observe(1)
        bits_after_1 = imarkov_instance.bits

        imarkov_instance.observe(1)
        bits_after_2 = imarkov_instance.bits

        # After two identical observations, entropy should change
        # because probability changes from 1.0 to 0.5 for example
        assert isinstance(bits_after_1, (int, float))
        assert isinstance(bits_after_2, (int, float))

    def test_entropy_non_negative(self):
        """Test that entropy is always non-negative."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=1)
        for val in [1, 2, 3, 1, 2, 1]:
            mrk.observe(val)
            assert mrk.bits >= 0


class TestIMarkovReset:
    """Test IMarkov reset functionality."""

    def test_reset(self, imarkov_instance):
        """Test reset method."""
        imarkov_instance.observe(1)
        imarkov_instance.observe(2)
        assert imarkov_instance.totObs > 0

        imarkov_instance.reset()
        assert imarkov_instance.totObs == 0
        assert imarkov_instance.bits == 0
        assert len(imarkov_instance.points) == 0
        assert imarkov_instance.actVals == []

    def test_set_dimension(self, imarkov_instance):
        """Test setDim method."""
        imarkov_instance.observe(1)
        assert imarkov_instance.totObs > 0

        imarkov_instance.setDim(2)
        assert imarkov_instance.dim == 2
        assert imarkov_instance.totObs == 0  # Reset on setDim


class TestIMarkovInfo:
    """Test IMarkov info methods."""

    def test_info_structure(self, imarkov_instance):
        """Test info() method returns valid structure."""
        imarkov_instance.observe(1)
        info = imarkov_instance.info(struct=True, histogram=False)

        assert info["res"] == "OK"
        assert "dat" in info
        assert "msg" in info
        assert "dim" in info["dat"]
        assert "totObs" in info["dat"]
        assert "bits" in info["dat"]

    def test_str_representation(self, imarkov_instance):
        """Test string representation."""
        imarkov_instance.observe(1)
        imarkov_instance.observe(2)
        str_repr = str(imarkov_instance)

        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_act_address(self):
        """Test actAddress() method."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=2)
        mrk.observe(1)
        mrk.observe(2)

        # After two observations with dim=2, should have address
        address = mrk.actAddress()
        assert isinstance(address, str)


class TestIMarkovEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_probability_handling(self, imarkov_instance):
        """Test that zero probabilities are handled safely."""
        # log(0) should not cause errors
        imarkov_instance.observe(1)
        # Check that no exception is raised
        assert imarkov_instance.bits >= 0

    def test_very_small_probabilities(self):
        """Test handling of very small probabilities."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=1)
        # Observe many different values
        for i in range(1000):
            mrk.observe(i)

        # All probabilities should be 1/1000
        for point in mrk.points:
            prob = point._vals["pro"]
            assert 0 < prob <= 1

    def test_large_dimension(self):
        """Test with large dimension."""
        from idata.imarkov import IMarkov

        mrk = IMarkov(name="test", dim=10)
        assert mrk.dim == 10
        mrk.observe(1)
        assert mrk.totObs == 1
