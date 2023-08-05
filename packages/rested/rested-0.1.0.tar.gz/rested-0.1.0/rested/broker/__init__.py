class Broker(object):
    """
    A broker acts against a resolved namespace by contacting external systems.
    """

    def run(self, ns):
        """
        Run the resolved namespace against the specified broker.
        """
        raise NotImplemented("run")
