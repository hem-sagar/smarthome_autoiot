from app.pipeline import run_pipeline
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["zero_shot", "one_shot"], default="zero_shot")
    args = parser.parse_args()
    run_pipeline(mode=args.mode)
