**DTKLPR lib wrapper**

- HowTo:
    - Use:
        ```
        from dtklp_wrapper import ImageEngine, Lib, EngineParams

        lib = Lib({LIB_PATH}, {BUFFER_SIZE})
        params = EngineParams()
        with params:
            #change settings
            engine = ImageEngine(lib, params)
            with engine:
                #use functions
        ```
    - Install:
        Just add repo link to requirements.txt file with *git+* ahead.
        For example: `git+https://git.pancir.it/egor.bakharev/DTKLP-wrapper.git`

- Useful links:
    - https://www.dtksoft.com/docs/lprsdk/