from projet.auth.security import hash_password, verify_password


def test_password_hash_and_verify():
    raw = "Test123!"
    h = hash_password(raw)
    assert h != raw
    assert verify_password(raw, h)
    assert not verify_password("Wrong123!", h)
