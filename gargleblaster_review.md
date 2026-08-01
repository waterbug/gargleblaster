# gargleblaster review (2026-08-01)

First review of the `gargleblaster` package — the last of the four in this
activity to be covered. It is small: 297 lines of Python, essentially
`gargleblaster/__main__.py` (230) and `gargleblaster/data.py` (65), plus
packaging (conda recipe, pyinstaller spec, Inno Setup templates) and two
doc-generation shell scripts.

Context taken as given (author): gargleblaster is a **local-environment-
specific wrapper** around `pangalactic.node`. Settings that would be defects
in a general-purpose package — the hardcoded `ldap_schema`, the GSFC download
url, the NASA-specific `org_code` handling it feeds — are appropriate here.
This review treats the wrapper role as correct and looks at how well it
performs it.

Some of `__main__.py` was already covered in `pangalactic.node`'s startup
review; those items are listed under "Carried forward" rather than
re-argued.

---

## Findings (most severe first)

### 1. A startup failure in a packaged build is completely silent
`gargleblaster/__main__.py:9-12`, and `main()` throughout

```python
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
```
This is correct for a windowed PyInstaller build, where `sys.stdout` and
`sys.stderr` genuinely are `None` — but it means **stderr is `/dev/null` for
the rest of the process**. `main()` then performs ~200 lines of setup (home
directory creation, four resource-copy steps, config assembly) with **no
`try`/`except` anywhere**, and none of it is logged: the orb's logging is not
started until `run()` is called at the very end.

So any exception raised during setup in a packaged Windows or macOS build
produces **no traceback, no log entry, and no dialog** — the application
simply fails to appear, with nothing anywhere to say why. On a developer's
console run the same failure is perfectly visible, which is exactly the shape
of problem that only ever manifests for end users.

Finding #2 is a concrete way to trigger it.

**STATUS: FIXED.** The former body of `main()` is now `start()`, and `main()`
wraps it in a `try`/`except BaseException` that calls a new
`report_startup_failure()` and exits 1. `SystemExit` is re-raised untouched,
so `--help` and argparse errors behave as before. The reporter:

1. writes the traceback to `sys.stderr` (a no-op against `os.devnull`, useful
   on a console run);
2. writes it to a timestamped `gargleblaster_startup_error_*.log` — in the app
   home directory when that is known, otherwise the system temp directory;
3. shows it in a `QMessageBox` with the traceback as detailed text, if a Qt
   application can be created at all.

The file is written **before** the GUI is attempted, deliberately: on a
headless machine constructing a `QApplication` can abort the process rather
than raise, and the log should already exist if it does.

A module-level `APP_HOME_DIR` is set as soon as the home directory is created,
so failures after that point report into the home directory where the user
will find them, and only earlier ones fall back to temp.

**Verified by execution** with a failure injected into `start()`:

| | result |
|---|---|
| `main()` exit code | 1 |
| traceback written to app home | yes, with both the exception text and a traceback |
| dialog | `'Gargleblaster startup failed'`, 376 chars of detail |
| failure *before* the home dir exists | falls back to the temp directory |

### 2. Adding any new subdirectory under `doc/` will break startup for every existing user
`gargleblaster/__main__.py:167-182`

```python
    if os.path.exists(doc_path):
        if os.path.exists(doc_dir):
            current_doc_files = set(os.listdir(doc_dir))
            gargleblaster_doc_files = set([s for s in os.listdir(doc_path) ...])
            docs_to_copy = gargleblaster_doc_files - current_doc_files
            for d in docs_to_copy:
                shutil.copy(os.path.join(doc_path, d), doc_dir)
        else:
            shutil.copytree(doc_path, doc_dir)
```
The first-run branch (`copytree`) handles subdirectories; the **incremental
branch does not** — `shutil.copy` raises `IsADirectoryError` when given one.

`doc/` **does** contain a subdirectory: `doc/images/`, and it is genuinely
packaged — `pyproject.toml` maps `"gargleblaster.doc.images" = "doc/images"`
with `package-data = ["*"]`, so the installed `gargleblaster/doc/` has it.

Today this is harmless: `images` was created by the first-run `copytree`, so
it is in `current_doc_files` and excluded from `docs_to_copy`. The hazard is
the **upgrade path** — a release that adds a *new* subdirectory under `doc/`
would put that directory into `docs_to_copy` for every user whose `docs/`
already exists, and startup would raise. The same applies if a user deletes
`docs/images` (which the comment at 178-181 explicitly invites as a way to
refresh the docs).

Per finding #1, in a packaged build that failure would be silent.

**STATUS: FIXED.** The two branches are replaced by a single
`shutil.copytree(doc_path, doc_dir, dirs_exist_ok=True)`, which handles the
first run and every later one, and handles subdirectories.

**A second bug surfaced while fixing this, and the same change fixes it.**
Comparing *names* (`gargleblaster_doc_files - current_doc_files`) meant an
**updated** doc file was never re-copied: only names that did not already
exist were. So documentation changes in a new release never reached any
existing user — the only way to get them was to delete the `docs` directory
by hand, which is what the old comment at 178-181 was really describing.
`copytree` with `dirs_exist_ok=True` overwrites, so the installed docs now
track the release. That is the intended behaviour for *distributed* docs
rather than user data, and is noted in the code so it is not mistaken for
carelessness.

**Verified by execution**, against a doc tree containing an `images/`
subdirectory and a stale `guide.html`:

| | subdirectory | stale doc refreshed |
|---|---|---|
| pre-fix | `IsADirectoryError: [Errno 21] Is a directory: .../doc/images` — startup aborts | no |
| post-fix | copied | yes |

Step [4] (test data) had the same latent shape and is now guarded with an
`os.path.isdir()` branch — deliberately *without* adopting the overwrite
behaviour, since a user's edits to a test data file should survive. It holds
a single file today, so that is a guard against a future addition rather than
a live bug.

### 3. The two `principals.json` files have already drifted
`gargleblaster/principals.json` vs
`pangalactic.vger/pangalactic/vger/test/principals.json`

Two copies of the crossbar authenticator's seed data are maintained in
separate repositories, and they are **already out of sync**: gargleblaster's
copy is missing `buckaroo`. (Verified by comparing the `authid`/`pubkey`
pairs.)

These are public keys, so this is not a disclosure problem — it is a
correctness one. The file seeds `principals.db` on the authenticator's first
start, so whichever copy is deployed determines which test users can log in,
and the answer depended on which repository the file was taken from.

**STATUS: FIXED — `gargleblaster/principals.json` removed** (author's
decision, 2026-08-01).
`pangalactic.vger/pangalactic/vger/test/principals.json` is authoritative, and
gargleblaster has no use for the file at all: it seeds the **crossbar
authenticator's** database, which is server-side setup, whereas gargleblaster
is the desktop client. Nothing in the gargleblaster repository referenced it —
verified: no code, no packaging entry, no script, only this review document.
It was an orphan copy that could only ever drift, and had.

For the record, the drift at the time of removal: the shared entries
(`zaphod`, `admin`, `vger`) had **identical** public keys, and gargleblaster's
copy was simply missing `buckaroo`. So the practical effect was that seeding
an authenticator from the wrong copy left `buckaroo` unable to log in, with
nothing to indicate why — the same silent-authentication-failure shape as the
trailing-newline bug in `pangalactic.node/admin_tool_review.md` #4.

### 4. The `--key` help text names the wrong default
`gargleblaster/__main__.py:104-106`

```python
    parser.add_argument('--key', dest='key', default='', type=str,
                    help="name of the file containing the user's private key"
                         ' [default: private.key]')
```
The actual default is computed in `pangalaxian.key_path`:
`self.app_base_name.lower() + '.key'` — i.e. **`gargleblaster.key`**, not
`private.key`. A user following the help text will look for, or create, the
wrong file.

This matters more than a typo normally would, because re-credentialing a user
who has lost their private key is a supported workflow (a user may have any
number of public keys registered against their userid), so people do go
looking for this file by name.

**STATUS: FIXED.** The help now names `gargleblaster.key` and says where it is
looked for, with a note tying it to `pangalaxian.key_path()` so the two stay
in step. **Verified by execution** — the real `--help` output:

```
  --key KEY          name of the file containing the user's private key,
                     looked for in the user's home directory [default:
                     "gargleblaster.key"]
```

That run incidentally confirms finding #1's `SystemExit` passthrough: `--help`
exits cleanly rather than being caught and reported as a startup failure.

### 5. `refdata.core += data.data` adds nothing
`gargleblaster/__main__.py:216-219`, `gargleblaster/data.py:8`

```python
    # [6] add application-specific (in this case, Gargleblaster-specific)
    # reference and test data to the pangalactic reference data
    refdata.core += data.data
```
`data.data` is `[]` and nothing in `data.py` appends to it — the file notes
"all Data Element Definitions are now in p.core.refdata". **Verified by
execution: this step adds 0 items.**

The line is therefore dead, while its comment claims an important-sounding
responsibility, which is worse than either being absent. The startup review
flagged it as a module-level-mutation hazard; it is in fact simply a no-op.
Either remove it, or keep it as an extension point with a comment saying that
is what it is.

`data.py`'s remaining live contribution is `schemas = {'MEL': mel_schema}` —
which raises a smaller point: `mel_schema` is built by intersecting the
hand-maintained `mel_deids` list with the `gsfc.mel` definitions found in
`refdata`, and anything in `mel_deids` with no matching definition is
**silently dropped** from the MEL. Currently 42 of 42 resolve, so this is
latent, but a typo in that list would remove a column from the MEL with no
warning. A one-line log of the difference would make it self-diagnosing.

**STATUS: FIXED (both parts).**

The `refdata.core +=` line is **kept as the extension point** — that is what
`data.py` is for — but guarded with `if data.data:` and given an honest
comment saying it currently adds nothing. The guard also removes the
module-level mutation hazard the startup review noted: an unconditional `+=`
would append a second copy of everything if `main()` ran twice in one process.
**Verified by execution**: with `data.data` empty, two calls leave
`refdata.core` unchanged; unguarded, two calls with a two-item list add four
entries.

`data.py` now computes `missing_mel_deids` and raises a `warnings.warn()`
naming them when the list is non-empty. `warnings` rather than logging because
this runs at import, before the orb's logger exists — and a typo in that list
is introduced during development, which is exactly where a warning is seen.
**Verified by execution**: 0 missing today so nothing is raised (42 of 42
resolve); with a deliberately mistyped id, the warning fires and names it.

Renumbering the step comment from `[6]` to `[5]` also closes the gap noted
under the carried-forward items — the steps now run [1]-[5].

### 6. `ug_to_garleblaster.sh` replaces only the first occurrence per line
`ug_to_garleblaster.sh`

```sh
sed s/Pangalaxian/Gargleblaster/g ... | \
    sed s/pangalaxian/gargleblaster/ | \
    sed s/PANGALAXIAN/Gargleblaster/ > doc/gargleblaster_user_guide.md
```
The second and third `sed` expressions are missing the `g` flag, so on any
line containing more than one lowercase or uppercase occurrence only the first
is rewritten, leaving "pangalaxian" in the generated user guide. Its sibling
`ref_to_gargleblaster.sh` uses `/g` throughout, so this is an inconsistency
rather than a deliberate choice.

(Also: the script's filename is missing a "g" — `ug_to_garleblaster.sh`.)

## Carried forward from `pangalactic.node/node_startup_review.md`

Still present in `__main__.py`, verified against the current source:

- ~~**`os.path.join(os.environ.get('USERPROFILE'))`**~~ and ~~**the
  unreachable cwd fallback**~~ — **both FIXED**, via the shared
  `p.core.get_user_home()` helper proposed in startup review #4. gargleblaster
  now does `user_home = get_user_home()` then
  `if user_home and os.path.exists(user_home):`, so no `None` reaches
  `os.path.exists()` and the "if all else fails" fallback is reachable.
  Verified by execution with both environment variables unset: pre-fix
  `TypeError`, post-fix `<cwd>/gargleblaster_home`. The same helper now serves
  `uberorb.start()`, `pangalaxian.run()` and the `Main.user_home` property —
  see `pangalactic.node/node_startup_review.md` #2 and #4.
- **Duplicated `makedirs`** (142-145) — the second is dead, and drops the
  explicit `mode=0o755`. Startup review #6.
- ~~**`release_mode = "dev"` is hardcoded**~~ — **FIXED.** It is now derived
  from the application version by a new `release_mode_for()`, so the build
  determines it and a production release no longer requires editing source:

  | version | release_mode | app_name | home directory |
  |---|---|---|---|
  | `4.4.dev3` | `dev` | `Gargleblaster_dev` | `gargleblaster_home_dev` |
  | `4.4rc1`, `4.4b2`, `4.4a1` | `test` | `Gargleblaster_test` | `gargleblaster_home_test` |
  | `4.4`, `4.4.1`, `5.0.post1` | `production` | `Gargleblaster` | `gargleblaster_home` |
  | `''`, `garbage`, `None` | `dev` | `Gargleblaster_dev` | `gargleblaster_home_dev` |

  An unparseable version falls back to `dev` deliberately: `dev` has its own
  home directory, so a bad version string cannot start the app against
  production user data. **Verified by execution** across all of the above; the
  current version yields `dev`, exactly as the hardcoded value did, so nothing
  changes until a non-dev version is built.

  **A related decision, since making `test` reachable exposed it.** The
  home-directory logic special-cased only `dev`, so a `test` release would
  have called itself `Gargleblaster_test` while falling through to the
  **production** home — a release candidate running against real user data.
  **Decided (author, 2026-08-01): release candidates use the test home.** The
  `test` branch now selects `gargleblaster_home_test`, so the app name and the
  home directory agree in every mode. The condition is
  `if TEST or release_mode == "test":` and is marked at the site so it is not
  later "simplified" back to `if TEST:`.
- Minor: the step comments run [1], [2], [3], [4], [6] — there is no [5].

## Smaller items

- **Duplicate imports**: `sys` and `os` are imported at 6-7 (needed before the
  stdout/stderr check) and again at 14 along with `argparse, shutil`. Harmless,
  but the second import of `os`/`sys` reads as an oversight rather than as the
  deliberate two-stage arrangement it is — worth a comment if kept.
- **`DEBUG`/`TEST` defaulting is inconsistent** (109-111):
  `config.get('debug')` has no default while `config.get('test', False)` does.
  Same effect, different shape.
- **`app_config['self_signed_cert'] = False`** (50) is a reasonable default,
  but note the test server in use (marvin) *does* use a self-signed cert, so
  this is a value users are expected to override in their config file. Worth
  a word in the README, since getting it wrong produces a TLS failure at
  connect time rather than anything self-explanatory.

## Verified correct / no findings

- **Step [3]'s `casroot` handling** (186-196) is correctly guarded by
  `sys.platform == 'win32'` and by `os.path.exists(casroot_path)`, and
  deliberately removes and recreates `casroot_home` so a stale copy cannot
  survive an upgrade — the one resource step that handles the upgrade case
  properly.
- **`data.py`'s MEL ordering logic** — `mel_schema` is built by iterating
  `mel_deids` and keeping those present in `gsfc_mel_deids`, so the MEL column
  order follows the hand-maintained list rather than whatever order `refdata`
  happens to yield. That is the intent, and it works.
- The argparse option set matches what `pangalaxian.run()` accepts, and
  `--key` is correctly typed as `str` here (unlike `pangalaxian.py`'s own
  `--key`, which was a boolean flag — startup review #1, since fixed).

## Status summary

**Fixed** (2026-08-01), both verified by execution and annotated inline:

- **#1** a startup failure is now reported — traceback to a log file in the
  app home (or temp), plus a dialog — instead of the application silently
  never appearing.
- **#2** the doc tree is copied with `copytree(dirs_exist_ok=True)`, which
  fixes both the subdirectory crash and the fact that updated docs never
  reached existing users. Step [4] made directory-safe too.

- **#4** the `--key` help now names the real default, `gargleblaster.key`.
- **#5** the `refdata.core +=` line is guarded and honestly commented, and
  `data.py` now warns when a MEL data element id has no matching definition
  instead of dropping it silently. (Step comments renumbered to [1]-[5],
  closing the carried-forward gap.)

- **`release_mode`** (carried forward) is now derived from the version, so a
  production build no longer needs a source edit.

- **#3** `gargleblaster/principals.json` removed; the vger test copy is
  authoritative and gargleblaster never needed one.

- **The `USERPROFILE` join and the unreachable cwd fallback** (carried
  forward) — fixed via the shared `p.core.get_user_home()` helper.

**Open:** #6 (the `sed` flags) and the duplicated `makedirs`.

## Suggested fix order

1. **#1 silent startup failure** — everything else that can go wrong at
   startup is invisible until this is addressed, in exactly the builds real
   users run.
2. **#2 the doc-copy upgrade hazard** — small fix (`dirs_exist_ok=True`), and
   it is a live trap for the next release that adds a doc subdirectory.
3. **#4 the `--key` default** and **#5 the dead `refdata` line** — both are
   one-line corrections to statements that are actively misleading.
4. **`release_mode`** (carried forward) — the blocker for producing a
   production build without editing source.
5. ~~**#3 the duplicated `principals.json`**~~ — done: removed, the vger
   test copy is authoritative.
6. **#6 the sed flags**, and the remaining carried-forward cleanups.
