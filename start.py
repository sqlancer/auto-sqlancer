#!/usr/bin/env python3
import os
import argparse
import sys
import json
from test import test_single, test_custom_dockerfile
from build import build_environment, build_sqlancer_image, build_db_image

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="AUTO-SQLancer")
    sub = parser.add_subparsers(dest="command", required=True)

    # test command
    test = sub.add_parser("test", help="Run SQLancer test")
    test.add_argument("--dbms", help="DBMS to test (e.g., mysql, postgres, or 'all')")
    test.add_argument("--config", help="Path to config.json for the DBMS")
    test.add_argument("--dockerfile", help="Path to custom Dockerfile for building DBMS image")
    test.add_argument("--cache", action="store_true", help="Use Docker cache when building image")
    # build command
    build = sub.add_parser("build", help="Build DBMS or SQLancer Docker image")
    build.add_argument("--dbms", help="DBMS to build (e.g., mysql, postgres, or 'all')")
    build.add_argument("--sqlancer", action="store_true", help="Build SQLancer image only")
    build.add_argument("--cache", action="store_true", help="Use Docker cache when building")

    args = parser.parse_args()
    use_cache = args.cache

    global_cfg = load_json("config.json")
    dbms_list = global_cfg.get("dbms_list", [])

    if args.command == "test":
        if args.dockerfile:
            if not args.config:
                parser.error("Custom DBMS test requires --config")
            cfg = load_json(args.config)
            cfg["image"] = f"{cfg['dbms']}-custom"
            cfg["container_name"] = f"{cfg['dbms']}-custom"
            build_environment(cfg, use_cache, True, args.dockerfile)
            test_custom_dockerfile(args.dockerfile, cfg, use_cache)

        elif args.dbms == "all":
            for dbms in dbms_list:
                config_path = os.path.join(dbms, "config.json")
                if not os.path.exists(config_path):
                    print(f"[WARNING] Skipping {dbms}, missing config file.")
                    continue
                cfg = load_json(config_path)
                build_environment(cfg, use_cache)
                test_single(cfg, use_cache)

        elif args.dbms:
            if not args.config:
                parser.error("Single DBMS test requires --config")
            cfg = load_json(args.config)
            build_environment(cfg, use_cache)
            test_single(cfg, use_cache)

        else:
            parser.error("Must specify either --dbms or --dockerfile")
    elif args.command == "build":
        if args.sqlancer:
            build_sqlancer_image(not use_cache)

        elif args.dbms == "all":
            for dbms in dbms_list:
                config_path = os.path.join(dbms, "config.json")
                if not os.path.exists(config_path):
                    print(f"[WARNING] Skipping {dbms}, missing config file.")
                    continue
                cfg = load_json(config_path)
                build_db_image(cfg, use_cache)
        elif args.dbms:
            config_path = os.path.join(args.dbms, "config.json")
            if not os.path.exists(config_path):
                print(f"[ERROR] Config file not found for DBMS: {args.dbms}")
                sys.exit(1)
            cfg = load_json(config_path)
            build_db_image(cfg, use_cache)

        else:
            parser.error("Must specify --dbms or --sqlancer for build command")

if __name__ == "__main__":
    main()
