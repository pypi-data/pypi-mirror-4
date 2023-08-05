import marionette

if __name__ == "__main__":
    m = marionette.Marionette()
    m.start_session()
    m.set_script_timeout(10000)
    m.execute_async_script("""
        setTimeout(foo, 100);
        marionetteScriptFinished(true);
        """)