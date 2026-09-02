from src.display import currency_info, usd_to_currency, convert_energy, convert_mass_flow


def test_currency_conversion_identity():
    assert usd_to_currency(100.0, "USD") == 100.0


def test_currency_conversion_changes_display_value():
    assert usd_to_currency(100.0, "INR", 83.0) == 8300.0


def test_energy_display_conversion():
    assert convert_energy(1000.0, "MWh/h", 8000) == 1.0
    assert convert_energy(1000.0, "GWh/y", 8000) == 8.0


def test_mass_flow_display_conversion():
    assert convert_mass_flow(1000.0, "t/h") == 1.0
    assert convert_mass_flow(1000.0, "t/d") == 24.0


def test_invalid_fx_rate_rejected():
    try:
        currency_info("USD", 0)
    except ValueError:
        return
    assert False, "Expected invalid FX rate to raise ValueError"
