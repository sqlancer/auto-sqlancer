#!/usr/bin/env python3
import argparse
import sys
from run_test import test_single, test_all, test_custom_dockerfile

def main():
    parser = argparse.ArgumentParser(description="AUTO-SQLancer")
    sub = parser.add_subparsers(dest="command", required=True)

    test = sub.add_parser("test", help="Run SQLancer test")
    test.add_argument("--dbms", help="DBMS to test (e.g., mysql, postgres, or 'all')")
    test.add_argument("--config", help="Path to config.json for the DBMS")
    test.add_argument("--dockerfile", help="Path to custom Dockerfile for building DBMS image")
    test.add_argument("--no-cache", action="store_true", help="Build image without Docker cache")
    test.add_argument("--cache", action="store_true", help="Use Docker cache when building image")

    args = parser.parse_args()

    if args.command == "test":
        if args.no_cache and args.cache:
            parser.error("Cannot use both --no-cache and --cache")

        use_cache = args.cache

        if args.dockerfile:
            if not args.config:
                parser.error("Custom DBMS test requires --config")
            test_custom_dockerfile(args.dockerfile, args.config, use_cache)

        elif args.dbms == "all":
            test_all(use_cache)

        elif args.dbms:
            if not args.config:
                parser.error("Single DBMS test requires --config")
            test_single(args.dbms, args.config, use_cache)

        else:
            parser.error("Must specify either --dbms or --dockerfile")

if __name__ == "__main__":
    main()
