import traceback

def f():
    try:
        1/2
        return
    except Exception as e:
        print traceback.format_exc()
    finally:
        print 'finally'

f()