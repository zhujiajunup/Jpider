def try_expect_finally():
    try:
        1/0
    except Exception:
        print 'e'
    finally:
        print 'finally'
try_expect_finally()
