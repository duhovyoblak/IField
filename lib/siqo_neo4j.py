#==============================================================================
# Siqo Neo4j interface library
#------------------------------------------------------------------------------
from neo4j         import GraphDatabase
from siqo_lib      import journal

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
NEO_URI = 'bolt://localhost:7687'

#==============================================================================
# package's variables
#------------------------------------------------------------------------------
connDEF = '_nil_'  # Neo4j driver

#==============================================================================
# Neo4j tools
#------------------------------------------------------------------------------
def openConn(usr, pas):

    global connDEF

    neo4j_driver = GraphDatabase.driver(NEO_URI, auth=(usr, pas), max_connection_lifetime=1000)

    journal.M('Neo4j.openConn: Connection was open for user {}'.format(usr))

    return neo4j_driver

#------------------------------------------------------------------------------
def commitConn(conn):

    journal.M('Neo4j.commitConn: Connection was closed')

#------------------------------------------------------------------------------
def init(usr, pas):

    global connDEF

    connDEF = openConn(usr, pas)

    journal.M('Neo4j.init: Library initialised for with user {}'.format(usr))

#==============================================================================
# Work with initialised Default DB
#------------------------------------------------------------------------------
def doQuerry(qry, **kwargs):

    global connDEF

    if connDEF == '_nil_':

        journal.M('Neo4j.doQuerry: ERROR Library is not initialised for qry {}'.format(qry.replace('\n', ' ')[:90]) )
        return '_nil_'

    else:

        with connDEF.session() as neo4j_session:
            result = neo4j_session.run(qry, **kwargs).data()

        journal.M('Neo4j.doQuerry: {}'.format(qry.replace('\n', ' ')[:90]))
        return result

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

#==============================================================================

#------------------------------------------------------------------------------
journal.M('Neo4j library ver 1.03')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
