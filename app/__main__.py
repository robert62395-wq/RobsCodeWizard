"""Launch Rob's Code Wizard via `python -m app`."""
import runpy
import sys
import traceback

if __name__ == "__main__":
    mod = None
    try:
        mod = runpy.run_module("app.main", run_name="__main__", alter_sys=True)
    except SystemExit:
        raise
    except BaseException:
        print("=" * 60)
        print("ERROR while launching Rob's Code Wizard via 'python -m app':")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        try:
            input("Press Enter to close...")
        except EOFError:
            pass
        sys.exit(1)

    # Defensive: if the module ran but never called run_app()
    # (no guard fired, or guard short-circuited), call it now.
    run_app = mod.get("run_app") if isinstance(mod, dict) else None
    if callable(run_app):
        try:
            rc = run_app()
        except SystemExit:
            raise
        except BaseException:
            print("=" * 60)
            print("ERROR inside run_app():")
            print("=" * 60)
            traceback.print_exc()
            print("=" * 60)
            try:
                input("Press Enter to close...")
            except EOFError:
                pass
            sys.exit(1)
        sys.exit(rc if isinstance(rc, int) else 0)
