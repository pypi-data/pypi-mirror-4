def start_ipymote():
    import os, sys
    if sys.platform.startswith("win32"):
        try:
            os.environ['VIRTUAL_ENV'] = os.environ['PYMOTE_ENV']
            os.environ['IPYTHONDIR'] = os.path.join(os.environ['PYMOTE_ENV'],'.ipython')
        except KeyError:
            pass
        
        from IPython.frontend.terminal.ipapp import TerminalIPythonApp
        app = TerminalIPythonApp.instance()
        app.initialize(argv=['--profile=pymote'])
        app.start()
    
    #TODO: support other platforms
    #elif sys.platform.startswith("linux2"):
    #elif sys.platform.startswith("darwin"):
