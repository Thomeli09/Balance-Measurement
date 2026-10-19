from balance_measurement import StorageCSV


def test_csv_measurements_round_trip(tmp_path):
    path = tmp_path / "measurements.csv"
    storage = StorageCSV(
        FilePath=path,
        FieldNames=["id", "weight"],
        FieldTypes=["int", "float"],
    )
    storage.DataAppend(Key=1, Value=[12.5])
    storage.Write()

    loaded = StorageCSV(FilePath=path)
    assert loaded.Read() == {1: [12.5]}
