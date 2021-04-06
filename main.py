import sshtunnel
import pymysql
import sys

show_db_query = "SHOW DATABASES"

show_tables_query = "SHOW TABLES"

all_user_query = "SELECT * FROM user_info"

get_user_query = "SELECT services FROM user_platforms WHERE acctID = ':acctID'"

update_user_services = "UPDATE user_platforms SET services = ':services' WHERE acctID = ':acctID'"


def update_services(sshuser, sshpass, dbpass, acctID, service):
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
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        userQuery = get_user_query.replace(":acctID", acctID)
        cursor.execute(userQuery)
        result = cursor.fetchone()

        # Append the new desired service
        currServices = result["services"]
        currServices += f",{service}"

        # Write the new desired service back to DB
        updateQuery = update_user_services.replace(":services", currServices)
        updateQuery = updateQuery.replace(":acctID", acctID)
        print(updateQuery)
        cursor.execute(updateQuery)

        connection.commit()
        connection.close()


def execute_query(sshuser, sshpass, dbpass, query):
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
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        for x in result:
            print(x)

        connection.close()


if __name__ == '__main__':
    sshuser = sys.argv[1]
    sshpass = sys.argv[2]
    dbpass = sys.argv[3]
    update_services(sshuser, sshpass, dbpass, "1", "TEST")
    #execute_query(sshuser, sshpass, dbpass, all_user_query)
