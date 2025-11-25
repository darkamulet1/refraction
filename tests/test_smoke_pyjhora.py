def test_pyjhora_imports():
    from jhora.horoscope.chart import charts
    from jhora.panchanga import drik
    assert charts is not None
    assert drik is not None
