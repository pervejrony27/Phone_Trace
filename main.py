import argparse
from modules import phone_info

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phone_Trace main")
    parser.add_argument("--number", required=True, help="Phone number to lookup")
    args = parser.parse_args()
    print(f"Running lookup for {args.number}")
