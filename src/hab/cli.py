"""Run python -m src.hab.cli --help. Writes require explicit local commands."""
import argparse
import json
from pathlib import Path
from .core import Store, apply_merge, plan_merge, rollback_merge, proof_record
from .revisions import compare_revisions, read_snapshot


def main():
    parser = argparse.ArgumentParser(description="IA Guardian Hab portable toolkit")
    parser.add_argument("--store", default="data/hab")
    commands = parser.add_subparsers(dest="command", required=True)
    intake = commands.add_parser("ingest")
    intake.add_argument("files", nargs="+")
    commands.add_parser("catalog")
    export = commands.add_parser("export")
    export.add_argument("source_ids", nargs="+")
    export.add_argument("--output", required=True)
    merge = commands.add_parser("plan")
    merge.add_argument("source_id")
    merge.add_argument("destination")
    merge.add_argument("--mappings", required=True, help="JSON object mapping source paths to destinations")
    merge.add_argument("--output", required=True)
    apply = commands.add_parser("apply")
    apply.add_argument("plan")
    apply.add_argument("--approve", required=True, help="Exact approval_sha256 from reviewed plan")
    apply.add_argument("--allow-conflicts", action="store_true")
    rollback = commands.add_parser("rollback")
    rollback.add_argument("--approve", required=True)
    proof = commands.add_parser("proof")
    proof.add_argument("asset")
    proof.add_argument("--acknowledgement", required=True)
    proof.add_argument("--consent", required=True)
    proof.add_argument("--output", required=True)
    reconcile = commands.add_parser("reconcile")
    reconcile.add_argument("previous")
    reconcile.add_argument("current")
    reconcile.add_argument("--max-age-hours", type=float, default=24)
    reconcile.add_argument("--output", help="Create a new review report; never overwrite an existing file")
    args = parser.parse_args()
    if args.command == "reconcile":
        result = compare_revisions(read_snapshot(args.previous), read_snapshot(args.current),
                                   max_age_hours=args.max_age_hours)
        rendered = json.dumps(result, indent=2)
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        print(rendered)
        return
    store = Store(args.store)
    if args.command == "ingest":
        result = [store.ingest(Path(f).name, Path(f).read_bytes()) for f in args.files]
    elif args.command == "catalog":
        result = store.sources()
    elif args.command == "export":
        Path(args.output).write_bytes(store.export(args.source_ids))
        result = {"output": args.output}
    elif args.command == "plan":
        result = plan_merge(store, args.source_id, args.destination,
                            json.loads(Path(args.mappings).read_text()))
        Path(args.output).write_text(json.dumps(result, indent=2))
    elif args.command == "apply":
        result = {"journal": str(apply_merge(store, json.loads(Path(args.plan).read_text()),
                                            args.approve, args.allow_conflicts))}
    elif args.command == "rollback":
        result = rollback_merge(store, args.approve)
    else:
        result = proof_record(Path(args.asset).read_bytes(), args.acknowledgement, args.consent)
        Path(args.output).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
