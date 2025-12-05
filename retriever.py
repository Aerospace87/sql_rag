import datasets
import json
from llama_index.core.schema import Document
from psycopg2 import connect


def load_guest_dataset() -> list:
    # Load the dataset
    guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")

    # Convert dataset entries into Document objects
    docs = [
        Document(
            text="\n".join([
                f"Name: {guest_dataset['name'][i]}",
                f"Relation: {guest_dataset['relation'][i]}",
                f"Description: {guest_dataset['description'][i]}",
                f"Email: {guest_dataset['email'][i]}"
            ]),
            metadata={"name": guest_dataset['name'][i]}
        )
        for i in range(len(guest_dataset))
    ]

    return docs


def get_connection_details(connection_file, source_name):
    """Function to read postgres db connection details from file"""
    with open(connection_file, 'r') as fh:
        data = json.load(fh)

        for source in data["sources"]:
            if source["source_name"] == source_name:
                return source["host"], source["port"], source["dbname"], source["user"], source["password"]




if __name__ == '__main__':
    host, port, dbname, user, password = get_connection_details("cred.json", "testdb")

    conn = connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

    cur = conn.cursor()

    query = """
        select
            *
        from public.articoli
        limit 10
    """

    res = cur.execute(query)

    print(cur.fetchall())

