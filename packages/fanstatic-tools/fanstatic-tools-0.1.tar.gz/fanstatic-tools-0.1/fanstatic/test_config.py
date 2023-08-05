from fanstatic.config import convert_config


def test_convert_config():
    d = {
        'versioning': 't',
        'recompute_hashes': 'false',
        'bottom': 'True',
        'force_bottom': 'False',
        'rollup': 0,
        'somethingelse': 'True',
        }
    assert convert_config(d) == {
        'versioning': True,
        'recompute_hashes': False,
        'bottom': True,
        'force_bottom': False,
        'rollup': False,
        'somethingelse': 'True',
        }
