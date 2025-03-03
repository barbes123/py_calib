class GlobalState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalState, cls).__new__(cls)
            cls._instance.save_results_to = None  # Initialize variable
        return cls._instance

state = GlobalState()  # Create a single instance