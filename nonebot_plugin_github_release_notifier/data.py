class Data:
    data = {}

    @classmethod
    def get(cls, key, default=None) :# -> Any | None:
        """Get the value associated with the key."""
        return cls.data.get(key, default)

    @classmethod
    def set(cls, key, value):
        """Set the value for the key."""
        cls.data[key] = value


data_set = Data()
