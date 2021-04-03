import sshtunnel
import pymysql
import sys
import pandas as pd


def database_connection(sshuser, sshpass, dbpass):
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=sshuser,
            ssh_password=sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }
        connection = pymysql.connect(**config)
        query = 'select version();'
        data = pd.read_sql_query(query, connection)
        print(data)
        connection.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sshuser = sys.argv[1]
    sshpass = sys.argv[2]
    dbpass = sys.argv[3]
    database_connection(sshuser, sshpass, dbpass)
