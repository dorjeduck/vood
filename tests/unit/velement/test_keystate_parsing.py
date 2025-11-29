"""Unit tests for keystate parsing"""

import pytest
from vood.velement.keystate_parser import (
    parse_element_keystates,
    parse_property_keystates,
)
from vood.velement.keystate import KeyState
from vood.component.state.circle import CircleState
from vood.transition.easing import linear, in_out
from vood.core.color import Color


@pytest.fixture
def state1():
    """First sample state"""
    return CircleState(x=0, y=0, radius=50)


@pytest.fixture
def state2():
    """Second sample state"""
    return CircleState(x=100, y=100, radius=75)


@pytest.fixture
def state3():
    """Third sample state"""
    return CircleState(x=200, y=200, radius=100)


@pytest.mark.unit
class TestElementKeystatesParsingBareStates:
    """Test parsing bare states (auto-distributed times)"""

    def test_parse_single_bare_state(self, state1):
        """Test parsing single bare state"""
        keystates = [state1]
        result = parse_element_keystates(keystates)

        assert len(result) == 1
        # Single state should be anchored at 0.0
        assert result[0].time == 0.0
        assert result[0].state is state1

    def test_parse_two_bare_states(self, state1, state2):
        """Test parsing two bare states"""
        keystates = [state1, state2]
        result = parse_element_keystates(keystates)

        assert len(result) == 2
        # Should span 0.0 to 1.0
        assert result[0].time == 0.0
        assert result[1].time == 1.0

    def test_parse_three_bare_states(self, state1, state2, state3):
        """Test parsing three bare states"""
        keystates = [state1, state2, state3]
        result = parse_element_keystates(keystates)

        assert len(result) == 3
        # Should be evenly distributed
        assert result[0].time == 0.0
        assert result[1].time == 0.5
        assert result[2].time == 1.0

    def test_parse_four_bare_states(self, state1, state2, state3):
        """Test parsing four bare states"""
        state4 = CircleState(x=300, y=300, radius=125)
        keystates = [state1, state2, state3, state4]
        result = parse_element_keystates(keystates)

        assert len(result) == 4
        # Should be evenly distributed
        assert result[0].time == 0.0
        assert abs(result[1].time - 1/3) < 0.001
        assert abs(result[2].time - 2/3) < 0.001
        assert result[3].time == 1.0


@pytest.mark.unit
class TestElementKeystatesParsingTuples:
    """Test parsing (time, state) tuples"""

    def test_parse_explicit_time_tuples(self, state1, state2, state3):
        """Test parsing tuples with explicit times"""
        keystates = [
            (0.0, state1),
            (0.5, state2),
            (1.0, state3),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 3
        assert result[0].time == 0.0
        assert result[1].time == 0.5
        assert result[2].time == 1.0

    def test_parse_partial_timeline(self, state1, state2):
        """Test parsing tuples that don't cover full timeline"""
        keystates = [
            (0.2, state1),
            (0.8, state2),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 2
        # Should respect explicit boundaries (not extend to 0.0/1.0)
        assert result[0].time == 0.2
        assert result[1].time == 0.8

    def test_parse_out_of_order_times(self, state1, state2, state3):
        """Test that out-of-order times are sorted"""
        keystates = [
            (1.0, state3),
            (0.0, state1),
            (0.5, state2),
        ]
        result = parse_element_keystates(keystates)

        # Should be sorted by time
        assert result[0].time == 0.0
        assert result[0].state is state1
        assert result[1].time == 0.5
        assert result[2].time == 1.0

    def test_parse_duplicate_times_uses_last(self, state1, state2):
        """Test that duplicate times use last definition"""
        keystates = [
            (0.0, state1),
            (0.0, state2),  # Duplicate time
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 1
        # Should use last definition at time 0.0
        assert result[0].state is state2


@pytest.mark.unit
class TestElementKeystatesParsingMixed:
    """Test parsing mixed bare states and tuples"""

    def test_parse_mixed_formats(self, state1, state2, state3):
        """Test parsing mix of bare states and tuples"""
        keystates = [
            state1,  # Bare (distributed between anchors)
            (0.5, state2),  # Explicit
            state3,  # Bare (distributed between anchors)
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 3
        # When mixing explicit and implicit, implicit times are distributed evenly between anchors
        assert result[0].time == 0.25  # Distributed between 0.0 and 0.5
        assert result[1].time == 0.5
        assert result[2].time == 0.75  # Distributed between 0.5 and 1.0

    def test_parse_implicit_between_explicit(self, state1, state2, state3):
        """Test implicit states distributed between explicit times"""
        state_middle = CircleState(x=50, y=50, radius=60)
        keystates = [
            (0.2, state1),
            state_middle,  # Should be placed at 0.5
            (0.8, state3),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 3
        assert result[0].time == 0.2
        assert result[1].time == 0.5  # Midpoint between 0.2 and 0.8
        assert result[2].time == 0.8

    def test_parse_multiple_implicit_between_explicit(self, state1, state2, state3):
        """Test multiple implicit states between explicit times"""
        state4 = CircleState(x=150, y=150, radius=80)
        keystates = [
            (0.0, state1),
            state2,
            state3,
            (1.0, state4),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 4
        assert result[0].time == 0.0
        assert abs(result[1].time - 1/3) < 0.001
        assert abs(result[2].time - 2/3) < 0.001
        assert result[3].time == 1.0


@pytest.mark.unit
class TestElementKeystatesParsingKeyStateObjects:
    """Test parsing KeyState objects"""

    def test_parse_keystate_objects(self, state1, state2):
        """Test parsing KeyState objects directly"""
        keystates = [
            KeyState(state=state1, time=0.0),
            KeyState(state=state2, time=1.0),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 2
        assert result[0].time == 0.0
        assert result[1].time == 1.0

    def test_parse_keystate_with_easing(self, state1, state2):
        """Test parsing KeyState objects with easing"""
        keystates = [
            KeyState(state=state1, time=0.0),
            KeyState(state=state2, time=1.0, easing={"x": in_out}),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 2
        assert result[1].easing == {"x": in_out}

    def test_parse_mixed_keystate_and_tuples(self, state1, state2, state3):
        """Test parsing mix of KeyState objects and tuples"""
        keystates = [
            KeyState(state=state1, time=0.0),
            (0.5, state2),
            KeyState(state=state3, time=1.0),
        ]
        result = parse_element_keystates(keystates)

        assert len(result) == 3
        assert all(isinstance(ks, KeyState) for ks in result)


@pytest.mark.unit
class TestPropertyKeystatesParsingBareValues:
    """Test parsing property keystates with bare values"""

    def test_parse_single_value(self):
        """Test parsing single property value"""
        keystates = [Color("#FF0000")]
        result = parse_property_keystates(keystates)

        # Should extend to cover full timeline
        # The parser creates anchors at 0.0 and 1.0, plus the implicit point between
        assert len(result) >= 2
        assert result[0][0] == 0.0
        assert result[-1][0] == 1.0

    def test_parse_two_values(self):
        """Test parsing two property values"""
        color1 = Color("#FF0000")
        color2 = Color("#00FF00")
        keystates = [color1, color2]
        result = parse_property_keystates(keystates)

        # Should span 0.0 to 1.0
        assert len(result) == 2
        assert result[0][0] == 0.0
        assert result[0][1] is color1
        assert result[1][0] == 1.0
        assert result[1][1] is color2

    def test_parse_three_values(self):
        """Test parsing three property values"""
        values = [100, 200, 300]
        keystates = values
        result = parse_property_keystates(keystates)

        assert len(result) == 3
        assert result[0][0] == 0.0
        assert result[1][0] == 0.5
        assert result[2][0] == 1.0


@pytest.mark.unit
class TestPropertyKeystatesParsingTuples:
    """Test parsing property keystates with tuples"""

    def test_parse_time_value_tuples(self):
        """Test parsing (time, value) tuples"""
        keystates = [
            (0.0, 100),
            (0.5, 200),
            (1.0, 300),
        ]
        result = parse_property_keystates(keystates)

        assert len(result) == 3
        assert result[0][0] == 0.0
        assert result[0][1] == 100

    def test_parse_partial_timeline_extends(self):
        """Test that property keystates always extend to full timeline"""
        keystates = [
            (0.3, 100),
            (0.7, 200),
        ]
        result = parse_property_keystates(keystates)

        # Should extend to 0.0 and 1.0
        assert len(result) == 4
        assert result[0][0] == 0.0
        assert result[0][1] == 100  # First value extended
        assert result[-1][0] == 1.0
        assert result[-1][1] == 200  # Last value extended

    def test_parse_time_value_easing_tuples(self):
        """Test parsing (time, value, easing) tuples"""
        keystates = [
            (0.0, 100, linear),
            (1.0, 200, in_out),
        ]
        result = parse_property_keystates(keystates)

        assert len(result) == 2
        assert result[0][2] is linear
        assert result[1][2] is in_out


@pytest.mark.unit
class TestPropertyKeystatesParsingMixed:
    """Test parsing mixed property keystate formats"""

    def test_parse_mixed_bare_and_tuples(self):
        """Test parsing mix of bare values and tuples"""
        keystates = [
            100,
            (0.5, 200),
            300,
        ]
        result = parse_property_keystates(keystates)

        # Should have full timeline coverage
        assert result[0][0] == 0.0
        assert result[-1][0] == 1.0


@pytest.mark.unit
class TestKeystateParsingEdgeCases:
    """Test edge cases in keystate parsing"""

    def test_parse_empty_keystates_raises(self):
        """Test that empty keystates list raises error"""
        with pytest.raises(ValueError, match="keystates cannot be empty"):
            parse_element_keystates([])

    def test_parse_empty_property_keystates_raises(self):
        """Test that empty property keystates list raises error"""
        with pytest.raises(ValueError, match="property keystates cannot be empty"):
            parse_property_keystates([])

    def test_parse_invalid_time_raises(self, state1):
        """Test that times outside 0.0-1.0 raise error"""
        with pytest.raises(ValueError, match="time must be between 0.0 and 1.0"):
            parse_element_keystates([(1.5, state1)])

        with pytest.raises(ValueError, match="time must be between 0.0 and 1.0"):
            parse_element_keystates([(-0.5, state1)])

    def test_parse_invalid_tuple_format_raises(self):
        """Test that invalid tuple format raises error"""
        with pytest.raises(ValueError, match="Invalid tuple format"):
            parse_element_keystates([(0.5, "not a state")])

    def test_parse_invalid_type_raises(self):
        """Test that invalid type raises error"""
        with pytest.raises(ValueError, match="Invalid keystate format"):
            parse_element_keystates(["invalid"])

    def test_parse_time_exactly_zero(self, state1):
        """Test parsing time exactly 0.0"""
        keystates = [(0.0, state1)]
        result = parse_element_keystates(keystates)
        assert result[0].time == 0.0

    def test_parse_time_exactly_one(self, state1):
        """Test parsing time exactly 1.0"""
        keystates = [(1.0, state1)]
        result = parse_element_keystates(keystates)
        assert result[0].time == 1.0

    def test_parse_very_close_times(self, state1, state2):
        """Test parsing times that are very close together"""
        keystates = [
            (0.5, state1),
            (0.500001, state2),
        ]
        result = parse_element_keystates(keystates)

        # Both should be preserved (different times)
        assert len(result) == 2

    def test_parse_many_keystates(self, state1):
        """Test parsing many keystates"""
        states = [CircleState(x=i*10, y=i*10, radius=50) for i in range(20)]
        result = parse_element_keystates(states)

        assert len(result) == 20
        # Should be evenly distributed
        for i, ks in enumerate(result):
            expected_time = i / 19  # 0.0 to 1.0 over 20 points
            assert abs(ks.time - expected_time) < 0.001


@pytest.mark.unit
class TestPropertyKeystateValueEasingTuples:
    """Test ambiguous (value, easing) tuple handling"""

    def test_parse_value_easing_tuple(self):
        """Test parsing (value, easing) tuple"""
        keystates = [
            (100, linear),  # Value with easing
            (200, in_out),
        ]
        result = parse_property_keystates(keystates)

        # Should extend to full timeline
        assert result[0][0] == 0.0
        assert result[-1][0] == 1.0
        # Easing should be preserved
        assert result[0][2] is linear


@pytest.mark.unit
class TestKeystateTimeDistribution:
    """Test time distribution algorithms"""

    def test_distribution_single_implicit_between_anchors(self, state1, state2, state3):
        """Test single implicit state placed at midpoint"""
        keystates = [
            (0.0, state1),
            state2,  # Implicit
            (1.0, state3),
        ]
        result = parse_element_keystates(keystates)

        assert result[1].time == 0.5

    def test_distribution_two_implicits_between_anchors(self, state1, state2, state3):
        """Test two implicit states evenly distributed"""
        state4 = CircleState(x=150, y=150, radius=80)
        keystates = [
            (0.0, state1),
            state2,  # Implicit
            state3,  # Implicit
            (1.0, state4),
        ]
        result = parse_element_keystates(keystates)

        # Should be at 1/3 and 2/3
        assert abs(result[1].time - 1/3) < 0.001
        assert abs(result[2].time - 2/3) < 0.001

    def test_distribution_uneven_segments(self, state1, state2, state3):
        """Test distribution in uneven segments"""
        state4 = CircleState(x=150, y=150, radius=80)
        keystates = [
            (0.0, state1),
            state2,  # Should be at 0.5 (midpoint of 0.0-1.0)
            (1.0, state4),
        ]
        result = parse_element_keystates(keystates)

        assert result[1].time == 0.5
