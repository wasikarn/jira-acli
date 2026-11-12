# _dry-run.sh — sourced, not run, by the acli-*.sh wrappers so --dry-run works in any
# argument position. Sets DRY_RUN=true|false and removes --dry-run from "$@": sourced
# with no arguments, so the `set --` below rewrites the caller's positional parameters.
DRY_RUN=false
_args=()
for _a in "$@"; do
  if [ "$_a" = "--dry-run" ]; then DRY_RUN=true; else _args+=("$_a"); fi
done
set -- ${_args[@]+"${_args[@]}"}
unset _a _args
