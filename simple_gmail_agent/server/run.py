import argparse
import uvicorn
from dotenv import load_dotenv

from simple_gmail_agent.server.api import create_app



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()
    uvicorn.run(
        app=create_app(),
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
