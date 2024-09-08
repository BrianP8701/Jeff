# Jeff: A supercharged Spotlight Replacement for Mac

## Built by Ayush Goel and Brian Przezdziecki

[Demo](https://youtu.be/w1Fz9iy0sbU)

![image](./jeff_sample.png)

Jeff indexes over your web browser history, your emails and your file system to generate embeddings on the content and provide more powerful and universal search capabilities than spotlight. 

We built this by using OPEN AIs word embeddings on all of the data contents and storing it in a local pgvector database to support fast embeddings search using l2 / cosine similarity.

## Running Instructions

Create a `.env` file following the `.env.example`. You will need your Gmail API keys to access your emails as well.

Quit Google Chrome if you are currently using it and run `ingestion.py` to read from your chrome history and build the indexing.

The ingestion script should also handle your emails and local file system (give permissions if needed).
git
Run the fast api server (located in `server/app.py`) using `uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload`.

Open up the Xcode project, and fill in the necessary signing and certificates. Then run the project and give permissions to open up files. 

Press `Command + J` and you should be ready to go with Jeff!
