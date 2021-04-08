from typing import Optional
from fastapi import FastAPI
from fastapi import HTTPException
import sshtunnel
import pymysql
import uvicorn
from pydantic import BaseSettings

get_user_query = "SELECT services FROM user_platforms WHERE acctID = ':acctID'"
update_user_services = "UPDATE user_platforms SET services = ':services' WHERE acctID = ':acctID'"
insert_user_sql = "INSERT INTO user_info (username, password, firstname, lastname, acctID) VALUES (%s, %s, %s, %s, %s)"
find_max_acctID_sql = "SELECT MAX(acctID) as maxID FROM user_info"


class Settings(BaseSettings):
    sshuser: str = "<FILL ME IN>"
    sshpass: str = "<FILL ME IN>"
    dbpass: str = "<FILL ME IN>"


settings = Settings()
app = FastAPI()


@app.get("/")
def read_root():
    raise HTTPException(status_code=404, detail="Invalid request url")


@app.get("/users")
def read_all_users():
    returnList = []
    query = "SHOW TABLES"
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
        cursor.execute(query)
        result = cursor.fetchall()
        for x in result:
            returnList.append(x)
        connection.close()

    return returnList


@app.put("/users/{user_id}")
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

        userQuery = get_user_query.replace(":acctID", user_id)
        cursor.execute(userQuery)
        result = cursor.fetchone()

        # Append the new desired service
        currServices = result["services"]
        currServices += f",{service}"

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
        maxID = result["maxID"]
        values = (username, password, firstname, lastname, maxID+1)
        cursor.execute(insert_user_sql, values)
        connection.commit()
        connection.close()

        return {"user_id": 1}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)