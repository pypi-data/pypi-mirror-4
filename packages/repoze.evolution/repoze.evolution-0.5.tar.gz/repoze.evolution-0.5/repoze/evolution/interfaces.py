from zope.interface import Interface

class IEvolutionManager(Interface):
    """Manager objects passed to 'evolve_to_latest' must provide this API.
    """

    def get_sw_version():
        """ Return the software version of the managed package.
        """

    def get_db_version():
        """ Return the database version of the managed package.
        """

    def evolve_to(version):
        """ Perform work to evolve to the integer ``version``.
        
        Responsible for setting the db version after a successful evolve.
        """
