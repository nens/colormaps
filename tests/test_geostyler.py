#!/usr/bin/env python3

import pytest
from colormaps.geostyler import (
    import_from_geostyler,
    extract_colormap_entries,
    hex_to_rgba,
)


# Test data fixtures
@pytest.fixture
def valid_geostyler():
    """Valid GeoStyler data for testing."""
    return                    {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "colorMap": {
                            "type": "ramp",
                            "colorMapEntries": [
                                {"color": "#6b0a5c", "quantity": -0.4, "label": "<= +0.40", "opacity": 1.0},
                                {"color": "#d7191c", "quantity": -0.2, "label": "+0.30 - +0.20", "opacity": 1.0},
                            ],
                        },
                    }
            


@pytest.fixture
def geostyler_with_transparency():
    """GeoStyler data with transparent entries for testing."""
    return  {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "colorMap": {
                            "type": "ramp",
                            "colorMapEntries": [
                                {"color": "#6b0a5c", "quantity": -0.4, "opacity": 1.0},
                                {"color": "#cccccc", "quantity": 0.01, "opacity": 0.0},
                                {"color": "#2b8337", "quantity": 100.0, "opacity": 1.0},
                            ],
                        },
                    }
    


@pytest.fixture
def geostyler_intervals():
    """GeoStyler data with intervals type for testing discrete colormaps."""
    return      {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "colorMap": {
                            "type": "intervals",
                            "colorMapEntries": [
                                {"color": "#6b0a5c", "quantity": -0.4, "opacity": 1.0},
                                {"color": "#d7191c", "quantity": -0.2, "opacity": 1.0},
                                {"color": "#2b8337", "quantity": 100.0, "opacity": 1.0},
                            ],
                        },
                    }

@pytest.fixture
def geostyler_values():
    """GeoStyler data with values type for testing discrete value colormaps."""
    return   {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "colorMap": {
                            "type": "values",
                            "colorMapEntries": [
                                {"color": "#ff0000", "quantity": 1, "opacity": 1.0},
                                {"color": "#00ff00", "quantity": 5, "opacity": 1.0},
                                {"color": "#0000ff", "quantity": 10, "opacity": 1.0},
                                {"color": "#ffff00", "quantity": 15, "opacity": 0.5},
                            ],
                        },
                    }
            

@pytest.fixture
def geostyler_with_labels():
    """GeoStyler data with labels for testing label extraction."""
    return      {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "colorMap": {
                            "type": "values",
                            "colorMapEntries": [
                                {"color": "#ff0000", "quantity": 1, "label": "Residential", "opacity": 1.0},
                                {"color": "#00ff00", "quantity": 2, "label": "BAG - woonfunctie", "opacity": 1.0},
                                {"color": "#0000ff", "quantity": 3, "label": "Commercial", "opacity": 1.0},
                                {"color": "#ffff00", "quantity": 4, "opacity": 1.0},  # No label
                            ],
                        },
                    }
 

@pytest.fixture
def geostyler_example():
    """Complete example GeoStyler data."""
    return {
                        "kind": "Raster",
                        "opacity": 1.0,
                        "channelSelection": {"grayChannel": {"sourceChannelName": "1"}},
                        "colorMap": {
                            "type": "ramp",
                            "extended": True,
                            "colorMapEntries": [
                                {"color": "#6b0a5c", "quantity": -0.4, "label": "<= +0.40", "opacity": 1.0},
                                {"color": "#d7191c", "quantity": -0.2, "label": "+0.30 - +0.20", "opacity": 1.0},
                                {"color": "#cccccc", "quantity": 0.01, "label": "+0.01 - -0.01", "opacity": 0.0},
                                {"color": "#2b8337", "quantity": 100.0, "label": ">-0.20", "opacity": 1.0},
                            ],
                        },
                    }


# hex_to_rgba tests
@pytest.mark.parametrize(
    "hex_color,opacity,expected",
    [
        ("#6b0a5c", 1.0, [107, 10, 92, 255]),
        ("#6b0a5c", 0.5, [107, 10, 92, 127]),
        ("#6b0a5c", 0.0, [107, 10, 92, 0]),
        ("#ffffff", 1.0, [255, 255, 255, 255]),
        ("#000000", 1.0, [0, 0, 0, 255]),
    ],
)
def test_hex_to_rgba_valid(hex_color, opacity, expected):
    """Test hex_to_rgba with valid inputs."""
    result = hex_to_rgba(hex_color, opacity)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_hex",
    [
        "6b0a5c",  # No hash
        "#6b0a5",  # Wrong length
        "#gggggg",  # Invalid characters
    ],
)
def test_hex_to_rgba_invalid(invalid_hex):
    """Test hex_to_rgba with invalid inputs."""
    with pytest.raises(ValueError, match="Invalid hex color format"):
        hex_to_rgba(invalid_hex)


# extract_colormap_entries tests
def test_extract_colormap_entries_valid(valid_geostyler):
    """Test extraction from valid structure."""
    entries, colormap_type = extract_colormap_entries(valid_geostyler)
    expected_entries = [
        {"color": "#6b0a5c", "quantity": -0.4, "label": "<= +0.40", "opacity": 1.0},
        {"color": "#d7191c", "quantity": -0.2, "label": "+0.30 - +0.20", "opacity": 1.0},
    ]
    assert entries == expected_entries
    assert colormap_type == "ramp"  # Default when no type specified


@pytest.mark.parametrize(
    "invalid_data,error_type,error_match",
    [
        (
            {"kind": "Point", "colorMap": {"colorMapEntries": []}},
            ValueError,
            "Expected Raster symbolizer",
        ),
    ],
)
def test_extract_colormap_entries_invalid(invalid_data, error_type, error_match):
    """Test extract_colormap_entries with invalid data."""
    with pytest.raises(error_type, match=error_match):
        extract_colormap_entries(invalid_data)


def test_import_from_geostyler_with_transparency(geostyler_with_transparency):
    """Test conversion including transparent entries."""
    result = import_from_geostyler(geostyler_with_transparency)

    # Check structure
    assert result["type"] == "GradientColormap"
    assert "data" in result

    # Check data (should have 3 entries, including transparent one)
    data = result["data"]
    assert len(data) == 3

    # Verify entries are sorted by quantity and include transparent entry
    expected_data = [
        [-0.4, [107, 10, 92, 255]],  # #6b0a5c, opacity 1.0
        [0.01, [204, 204, 204, 0]],  # #cccccc, opacity 0.0 (transparent)
        [100.0, [43, 131, 55, 255]],  # #2b8337, opacity 1.0
    ]
    assert data == expected_data

    # Check free attribute
    assert result["free"] is False


# Integration test
def test_full_conversion_integration(geostyler_example):
    """Test complete conversion with extended GeoStyler data."""
    result = import_from_geostyler(geostyler_example)

    # Verify structure and entry count
    assert result["type"] == "GradientColormap"
    assert len(result["data"]) == 4

    # Verify sorting and all positions are preserved
    positions = [entry[0] for entry in result["data"]]
    expected_positions = [-0.4, -0.2, 0.01, 100.0]
    assert positions == expected_positions

    # Verify transparent entry is included with correct alpha
    transparent_entry = result["data"][2]  # 0.01 position
    assert transparent_entry[1][3] == 0  # Alpha channel should be 0


# Intervals colormap tests
def test_convert_geostyler_intervals_type(geostyler_intervals):
    """Test conversion with intervals type creates discrete bands."""
    result = import_from_geostyler(geostyler_intervals)

    # Should create duplicated entries for discrete bands
    expected_data = [
        [-0.4, [107, 10, 92, 255]],
        [-0.4, [215, 25, 28, 255]],
        [-0.2, [215, 25, 28, 255]],
        [-0.2, [43, 131, 55, 255]],
    ]

    assert result["type"] == "GradientColormap"
    assert result["data"] == expected_data
    assert result["free"] is False


def test_extract_colormap_entries_with_intervals_type(geostyler_intervals):
    """Test extraction returns correct type for intervals."""
    entries, colormap_type = extract_colormap_entries(geostyler_intervals)

    assert colormap_type == "intervals"
    assert len(entries) == 3


def test_convert_geostyler_values_type(geostyler_values):
    """Test conversion with values type creates discrete colormap."""
    result = import_from_geostyler(geostyler_values)

    # Should create DiscreteColormap with each entry present
    expected_data = [
        [1, [255, 0, 0, 255]],  # Red, quantity 1
        [5, [0, 255, 0, 255]],  # Green, quantity 5
        [10, [0, 0, 255, 255]],  # Blue, quantity 10
        [15, [255, 255, 0, 127]],  # Yellow with 50% opacity, quantity 15
    ]

    assert result["type"] == "DiscreteColormap"
    assert result["data"] == expected_data


def test_extract_colormap_entries_with_values_type(geostyler_values):
    """Test extraction returns correct type for values."""
    entries, colormap_type = extract_colormap_entries(geostyler_values)

    assert colormap_type == "values"
    assert len(entries) == 4


def test_convert_geostyler_with_labels(geostyler_with_labels):
    """Test conversion preserves labels in the correct format."""
    result = import_from_geostyler(geostyler_with_labels)

    # Should create DiscreteColormap
    assert result["type"] == "DiscreteColormap"

    # Should include labels in the correct format
    expected_labels = {"nl_NL": [[1, "Residential"], [2, "BAG - woonfunctie"], [3, "Commercial"]]}
    assert result["labels"] == expected_labels

    # Verify data is still correct
    expected_data = [
        [1, [255, 0, 0, 255]],  # Red
        [2, [0, 255, 0, 255]],  # Green
        [3, [0, 0, 255, 255]],  # Blue
        [4, [255, 255, 0, 255]],  # Yellow
    ]
    assert result["data"] == expected_data
