from balance_measurement import PlotParameters, Scale, StorageCSV
from balance_measurement import PlotParameters, Scale, StorageCSV
from balance_measurement.scale.ScaleBench import SerialScale


def test_package_public_api_is_available():
    assert Scale is not None
    assert StorageCSV is not None
    assert PlotParameters is not None


def test_scale_response_weight_parsing():
    assert SerialScale._ParseWeight("S S 12.345 g") == 12.345
    assert SerialScale._ParseWeight("GS +1.25E-2 g") == 0.0125
    assert SerialScale._ParseWeight("No stable value") is None
