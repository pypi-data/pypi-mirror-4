'''
Created on 23 sept. 2010

@author: coissac
'''
import psycopg2 

from obitools.ecobarcode.taxonomy import EcoTaxonomyDB

def addEcoBarcodeDBOption(optionManager):
    optionManager.add_option('--dbname',
                             action="store", dest="ecobarcodedb",
                             type='str',
                             default=None,
                             help="Specify the name of the ecobarcode database")

    optionManager.add_option('--server',
                             action="store", dest="dbserver",
                             type='str',
                             default="localhost",
                             help="Specify the adress of the ecobarcode database server")

    optionManager.add_option('--user',
                             action="store", dest="dbuser",
                             type='str',
                             default='postgres',
                             help="Specify the user of the ecobarcode database")

    optionManager.add_option('--port',
                             action="store", dest="dbport",
                             type='str',
                             default=5432,
                             help="Specify the port of the ecobarcode database")

    optionManager.add_option('--passwd',
                             action="store", dest="dbpasswd",
                             type='str',
                             default='',
                             help="Specify the passwd of the ecobarcode database")

    optionManager.add_option('--primer',
                             action="store", dest="primer",
                             type='str',
                             default=None,
                             help="Specify the primer used for amplification")
    
    
def ecobarcodeDatabaseConnection(options):
    if options.ecobarcodedb is not None:
        connection = psycopg2.connect(database=options.ecobarcodedb, 
                                      user=options.dbuser, 
                                      password=options.dbpasswd,
                                      host=options.dbserver,
                                      port=options.dbport)
        options.dbname=options.ecobarcodedb
    else:
        connection=None
    if connection is not None:
        options.ecobarcodedb=connection
        taxonomy = EcoTaxonomyDB(connection)
    else:
        taxonomy=None
    return taxonomy
    
