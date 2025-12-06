from ..processing.clean import run as clean
from ..processing.transform import run as transform
from ..features.build import run as build

def run():
    clean()
    transform()
    build()
    print("make_features: OK")

def main():
    run()

if __name__ == "__main__":
    main()