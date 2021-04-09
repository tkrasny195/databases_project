from typing import Optional
from fastapi import FastAPI
from fastapi import HTTPException
import sshtunnel
import pymysql
import uvicorn
from pydantic import BaseSettings

all_users_query = "Select username FROM user_info"
get_services_query = "SELECT services FROM user_platforms WHERE acctID = '%s'"
update_user_services = "UPDATE user_platforms SET services = ':services' WHERE acctID = ':acctID'"
insert_user_sql = "INSERT INTO user_info (username, password, firstname, lastname, acctID) VALUES (%s, %s, %s, %s, %s)"
insert_user_platform = "INSERT INTO user_platforms (acctID, services) VALUES (%s, %s)"
find_max_acctID_sql = "SELECT MAX(acctID) as maxID FROM user_info"
user_watchlist_query = "SELECT primaryTitle FROM watchlist WHERE acctID = '%s' AND removed <> '1'"
user_watchlist_remove_show = "UPDATE watchlist SET removed = '1' WHERE primaryTitle = '%s' AND acctID = '%s'"
user_watchlist_remove_all = "UPDATE watchlist SET removed = '1' WHERE acctID = '%s'"


class Settings(BaseSettings):
    sshuser: str = "<>"
    sshpass: str = "<>"
    dbpass: str = "<>"


settings = Settings()
app = FastAPI()


@app.get("/")
def read_root():
    raise HTTPException(status_code=404, detail="Invalid request url")


@app.get("/users")
def read_all_users():
    returnList = []
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute(all_users_query)
        result = cursor.fetchall()
        for x in result:
            returnList.append(x)
        connection.close()

    return returnList


@app.put("/users/services/{user_id}")
def update_services(user_id: str, service: str):
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }

        connection = pymysql.connect(**config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(get_services_query % user_id)
        result = cursor.fetchone()

        # Append the new desired service
        if result is not None and result["services"] is not None:
            currServices = result["services"]
            currServices += f",{service}"
        else:
            currServices = ""
            currServices += f"{service}"
        # Write the new desired service back to DB
        updateQuery = update_user_services.replace(":services", currServices)
        updateQuery = updateQuery.replace(":acctID", user_id)
        print(updateQuery)
        cursor.execute(updateQuery)
        connection.commit()

        connection.close()

        return {"user_id": user_id, "services": currServices}


@app.post("/users")
def create_user(username: str, password: str, firstname: str, lastname: str):
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }

        connection = pymysql.connect(**config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # When setting the new user's acctID, it should be greater than the previous highest.
        cursor.execute(find_max_acctID_sql)
        result = cursor.fetchone()
        acctID = result["maxID"] + 1

        values = (username, password, firstname, lastname, acctID)
        cursor.execute(insert_user_sql, values)

        # Add user to user_platforms table as well
        cursor.execute(insert_user_platform, (acctID, None))

        connection.commit()
        connection.close()

        return {"username": username, "password": password, "firstname": firstname, "lastname": lastname, "id": acctID}


@app.get("/users/services/{user_id}")
def read_user_services(user_id: str):
    returnList = []
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute(get_services_query % user_id)
        result = cursor.fetchall()
        for x in result:
            returnList.append(x)
        connection.close()

    return returnList


@app.get("/users/watchlist/{user_id}")
def read_user_watchlist(user_id: str):
    returnList = []
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute(user_watchlist_query % user_id)
        result = cursor.fetchall()
        for x in result:
            returnList.append(x)
        connection.close()

    return returnList


@app.delete("/users/watchlist/{user_id}", status_code=200)
def delete_watchlist(user_id: str, title: Optional[str] = None):
    with sshtunnel.SSHTunnelForwarder(
            ("129.74.154.187", 22),
            ssh_username=settings.sshuser,
            ssh_password=settings.sshpass,
            remote_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        config = {
            'user': "smanfred",
            'password': settings.dbpass,
            'host': "127.0.0.1",
            'port': tunnel.local_bind_port,
            'database': "smanfred"
        }

        connection = pymysql.connect(**config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        if title:
            # Delete just one show from watchlist when title is specified
            cursor.execute(user_watchlist_remove_show % (title, user_id))

        else:
            # Clear entire watchlist when no title specified
            cursor.execute(user_watchlist_remove_all % user_id)

        connection.commit()
        connection.close()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)