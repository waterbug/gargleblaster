#!/usr/bin/env python
"""
Gargleblaster gui application
"""
# to ensure no output unless specified ...
import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import argparse, os, shutil, sys
import tempfile, traceback
from datetime import datetime

from packaging.version import InvalidVersion, Version

import gargleblaster
from gargleblaster import __version__ as app_version
from gargleblaster import data
from gargleblaster.test import data as gargleblaster_test_data_mod


# set as soon as it is known, so that a startup failure after that point can
# report itself somewhere the user will be able to find
APP_HOME_DIR = ''


def release_mode_for(version):
    """
    Determine the release mode from the application version.

    The version is the single source of truth for this, so that the build
    determines the release mode and producing a production release does not
    require editing source.  It was previously the literal string "dev", which
    made the "test" and production branches unreachable and meant the
    application was always "Gargleblaster_dev" -- including the name of its
    home directory, so a production build would not have found the data of
    users who had been running it.

        4.4.dev3   -> "dev"          (a development version)
        4.4rc1     -> "test"         (any other pre-release: a, b, rc)
        4.4        -> "production"

    NOTE: an unparseable version falls back to "dev" deliberately.  "dev" uses
    its own home directory, so a bad version string cannot cause the app to
    start up against production user data.

    Args:
        version (str):  the application version

    Returns:
        str:  "dev", "test" or "production"
    """
    try:
        v = Version(version or '')
    except InvalidVersion:
        return 'dev'
    if v.dev is not None:
        return 'dev'
    if v.is_prerelease:
        return 'test'
    return 'production'


def report_startup_failure(exc_info):
    """
    Report a failure that occurred before the gui was up.

    NOTE: this exists because of the stdout/stderr redirection at the top of
    this module.  In a windowed PyInstaller build sys.stdout and sys.stderr
    really are None, so they are pointed at os.devnull -- which also means a
    traceback printed after that point goes nowhere.  Setup then runs for
    ~200 lines before run() starts the orb's logging, so without this an
    exception in that window produced no traceback, no log entry and no
    dialog:  the application simply never appeared, with nothing anywhere to
    say why.

    Args:
        exc_info (tuple):  the sys.exc_info() triple to report

    Returns:
        str:  path the traceback was written to, or '' if it could not be
            written anywhere
    """
    text = ''.join(traceback.format_exception(*exc_info))
    # last resort, in case even the file write fails -- harmless (and
    # invisible) when stderr is os.devnull, useful on a console run
    sys.stderr.write(text)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f'gargleblaster_startup_error_{stamp}.log'
    fpath = ''
    # prefer the app home directory (the user can find it, and it is where
    # the rest of the app's logs live); fall back to the system temp
    # directory if startup failed before the home directory existed
    for d in (APP_HOME_DIR, tempfile.gettempdir()):
        if not d or not os.path.isdir(d):
            continue
        try:
            candidate = os.path.join(d, fname)
            with open(candidate, 'w') as f:
                f.write(text)
            fpath = candidate
            break
        except Exception:
            continue
    # show it if a gui is possible at all -- for a windowed build this is the
    # only channel the user has
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        msg = 'Gargleblaster could not start.'
        if fpath:
            msg += f'\n\nDetails were written to:\n{fpath}'
        box = QMessageBox(QMessageBox.Critical,
                          'Gargleblaster startup failed', msg,
                          QMessageBox.Ok)
        box.setDetailedText(text)
        box.exec_()
    except Exception:
        # no gui available -- the file (and stderr) are all we have
        pass
    return fpath


def main():
    """
    Start Gargleblaster, reporting any failure that happens before the gui is
    up (see report_startup_failure()).
    """
    try:
        start()
    except SystemExit:
        # argparse --help / bad args, and our own exit below:  not a failure
        raise
    except BaseException:
        report_startup_failure(sys.exc_info())
        sys.exit(1)


def start():
    # NOTE: these are imported here rather than at module scope so that an
    # import failure is caught by main()'s handler and reported, rather than
    # happening at import time when nothing is watching
    from pangalactic.core import config, get_user_home, refdata, state
    from pangalactic.node.pangalaxian import run
    # NOTE: pangalactic.core.test[data|vault] and pangalactic.core.ontology
    # need to be imported here so that if we are running the "pyinstaller"
    # installed version of gargleblaster, the data files in those modules can
    # be accessed.
    import pangalactic.core.ontology
    import pangalactic.core.test.data
    import pangalactic.core.test.vault
    app_config = {}
    app_config['app_base_name'] = 'Gargleblaster'
    # derived from the version -- see release_mode_for().  For the current
    # version ("4.4.dev3") this is "dev", exactly as the hardcoded value was,
    # so nothing changes until a non-dev version is built.
    release_mode = release_mode_for(app_version)
    # config:  localized settings; user can edit
    # default configuration:
    if release_mode == 'dev':
        app_config['app_name'] = 'Gargleblaster_dev'
        # dev host
    elif release_mode == 'test':
        app_config['app_name'] = 'Gargleblaster_test'
        # dev host
    else:
        # "production" release
        app_config['app_name'] = 'Gargleblaster'
        # production host
    # self_signed_cert -> the server's cert is self-signed, so it must be
    # present in the home directory as the server_cert.pem file; if the
    # server has a CA-signed cert, server_cert.pem will be ignored if present
    app_config['self_signed_cert'] = False
    # map from LDAP search dialog field display names to "dir_info" fields
    app_config['ldap_schema'] = {'OID': 'oid',
                                 'userid': 'id',
                                 'First Name': 'first_name',
                                 'Last Name': 'last_name',
                                 'MI or Name': 'mi_or_name',
                                 'Email': 'email',
                                 'Employer': 'employer_name'
                                 }
    # these state items are used to populate default prefs, and can later be
    # reverted to ...
    # 2018-03-26: per MDL, add h, w, d to default parameters
    # 2021-03-16: per MDL, add Temp. parms to default parameters
    state['app_default_parms'] = [
            'm', 'm[CBE]', 'm[Ctgcy]', 'm[MEV]',
            'P', 'P[CBE]', 'P[Ctgcy]', 'P[MEV]',
            'P[peak]', 'P[standby]', 'P[survival]',
            'T[operational_max]', 'T[operational_min]',
            'T[survival_max]', 'T[survival_min]',
            'R_D', 'R_D[CBE]', 'R_D[Ctgcy]', 'R_D[MEV]',
            'height', 'width', 'depth', 'Cost']
    state['app_default_data_elements'] = [
            'Vendor',
            'TRL',
            'reference_missions'
            ]
    state['default_schema_name'] = 'MEL'
    state['p_defaults'] = {'m[ctgcy]': '0.30',
                           'P[ctgcy]': '0.30',
                           'R[ctgcy]': '0.30'}
    state['de_defaults'] = {}
    # download url (internal to GSFC network)
    u = 'https://nasa.sharepoint.com/teams/585public/Shared%20Documents/'
    u += 'Forms/AllItems.aspx'
    state['app_download_url'] = u
    # ------------------------------------------------------------------------
    # NOTE: the following section may not be needed now
    # -------------------------------------------------------------
    # check if we are installed (PyInstaller's "frozen")
    # installed = False
    # if getattr(sys, 'frozen', False):
        # installed = True
    # -------------------------------------------------------------
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true",
                        help="debug mode")
    parser.add_argument("-t", "--test", action="store_true",
                        help="test mode")
    parser.add_argument("-u", "--unencrypted", action="store_true",
                        help="use unencrypted transport (no tls)")
    parser.add_argument('--auth', dest='auth', type=str, default='cryptosign',
                        help='authentication method: "ticket" or "cryptosign" '
                             '[default: "cryptosign" (pubkey auth)]')
    # NOTE: the default named here must match what pangalaxian.key_path()
    # actually computes -- "app_base_name.lower() + '.key'" -- which for this
    # app is "gargleblaster.key".  It previously said "private.key", which is
    # not a name the application ever uses, and this is a file users go
    # looking for by name (a user may have several key pairs registered
    # against their userid, so replacing a lost key is a normal operation).
    parser.add_argument('--key', dest='key', default='', type=str,
                    help="name of the file containing the user's private key,"
                         " looked for in the user's home directory"
                         ' [default: "gargleblaster.key"]')
    args = parser.parse_args()
    # use True for DEBUG default setting (SCW 2018-12-23) ...
    DEBUG = config.get('debug') or args.debug
    # use True for TEST to load test data (SCW 2025-01-19) ...
    TEST = config.get('test', False) or args.test
    # use tls unless testing in a non-secure env
    TLS = config.get('tls', True)
    if args.unencrypted:
        # cmd line arg overrides config
        TLS = False
    # create a gargleblaster home directory in the user's home dir
    app_home_dir = ''
    # NOTE: the platform branch that used to be inlined here now lives in
    # p.core.get_user_home(), shared with orb.start() and pangalaxian.run().
    # This also makes the "if all else fails" fallback below reachable: the
    # old code did os.path.exists(user_home) with a possibly-None user_home,
    # which raised TypeError before the fallback could be reached.
    user_home = get_user_home()
    if user_home and os.path.exists(user_home):
        if TEST or release_mode == "test":
            # ----------------------------------------------------------------
            # NOTE: "release_mode == 'test'" was added along with deriving
            # release_mode from the version.  Previously release_mode was
            # hardcoded to "dev", so a "test" release could not occur and this
            # branch only ever saw the --test flag.  Now that a pre-release
            # version (e.g. "4.4rc1") yields release_mode "test", this keeps
            # the home directory consistent with the app name: without it a
            # release candidate would call itself "Gargleblaster_test" while
            # using the *production* home directory below -- i.e. running
            # against real user data.
            #
            # DECIDED (author, 2026-08-01): release candidates use the test
            # home.  Do not "simplify" this back to "if TEST:".
            # ----------------------------------------------------------------
            app_home_dir = os.path.join(user_home, 'gargleblaster_home_test')
        elif release_mode == "dev":
            # for dev release, make home dir 'gargleblaster_home_dev'
            app_home_dir = os.path.join(user_home, 'gargleblaster_home_dev')
        else:
            # for production release, make home dir 'gargleblaster_home'
            app_home_dir = os.path.join(user_home, 'gargleblaster_home')
    # if all else fails, create 'gargleblaster_home' inside the current
    # directory -- not desirable because 'gargleblaster_home' holds user data
    # that needs to persist when a new version of the client is "installed",
    # which typically destroys the current directory.  TODO:  generate warnings
    # if this option is used.
    if not app_home_dir:
        app_home_dir = os.path.join(os.getcwd(), 'gargleblaster_home')
    # NOTE: a second, identical "if not exists: makedirs(app_home_dir)" used to
    # follow this one.  It was unreachable -- the directory exists by then --
    # and it omitted mode=0o755, so if it ever had run it would have created
    # the home directory at the process umask instead.
    if not os.path.exists(app_home_dir):
        os.makedirs(app_home_dir, mode=0o755)
    # record it for report_startup_failure(), so that a failure from here on
    # is written where the user can find it rather than to a temp directory
    global APP_HOME_DIR
    APP_HOME_DIR = app_home_dir
    # update empty 'config' with app_config ... anything in this config can be
    # overridden by user edits to the config file (loaded by Pangalaxian)
    config.update(app_config)
    ##########################################################################
    # The following steps [1]-[7] copy files into known locations within the
    # app_home directory -- a bit messy, but it works
    ##########################################################################
    # [1] create a "vault" directory in app_home
    vault_dir = os.path.join(app_home_dir, 'vault')
    if not os.path.exists(vault_dir):
        os.makedirs(vault_dir, mode=0o755)
    # [2] copy doc files from doc_path** into app_home_dir
    #     ** NOTE: doc_path will only exist if gargleblaster has been
    #     installed
    #     (a) as a conda package or
    #     (b) as a pyinstaller dist
    #     ... i.e., it is not part of the gargleblaster module but is copied
    #     into it by running setup.py, conda build, or pyinstaller)
    gargleblaster_mod_path = gargleblaster.__path__[0]
    doc_path = os.path.join(gargleblaster_mod_path, 'doc')
    doc_dir = os.path.join(app_home_dir, 'docs')
    if os.path.exists(doc_path):
        # --------------------------------------------------------------------
        # NOTE: one copytree with dirs_exist_ok=True handles both the first run
        # and every later one.  This replaces a per-entry shutil.copy() of
        # whatever names were missing from "docs", which had two problems:
        #
        # [a] shutil.copy() raises IsADirectoryError when handed a directory,
        #     and doc/ ships one ("images", installed as
        #     gargleblaster.doc.images -- see pyproject.toml).  It happened not
        #     to bite only because "images" was created by the first-run
        #     copytree and so was never in the set of missing names; adding any
        #     *new* doc subdirectory in a release would have raised for every
        #     user whose "docs" already existed -- silently, in a packaged
        #     build (see report_startup_failure()).
        #
        # [b] comparing *names* meant an updated doc file was never re-copied,
        #     so documentation changes in a new release only ever reached users
        #     who deleted their "docs" directory by hand.
        #
        # These are distributed docs rather than user data, so overwriting them
        # is the intended behaviour:  the installed copy should track the
        # release.  Anything a user wants to keep should not live here.
        # --------------------------------------------------------------------
        shutil.copytree(doc_path, doc_dir, dirs_exist_ok=True)
    # [3] if we are running on Windows as a pyinstaller dist, there will
    #     be a 'casroot' directory that contains files needed by pythonocc --
    #     copy them to home and set "CASROOT" env var ...
    if sys.platform == 'win32':
        casroot_path = os.path.join(gargleblaster_mod_path, 'casroot')
        casroot_home = os.path.join(app_home_dir, 'casroot')
        if os.path.exists(casroot_path):
            # copy all casroot files to home dir at startup
            if os.path.exists(casroot_home):
                # if casroot_home already exists, remove it so it can be
                # recreated
                shutil.rmtree(casroot_home, ignore_errors=True)
            shutil.copytree(casroot_path, casroot_home)
            os.environ['CASROOT'] = casroot_home
    # [4] copy test data files from gargleblaster.test.data into the
    # "test_data" dir
    test_data_dir = os.path.join(app_home_dir, 'test_data')
    current_test_files = set()
    if os.path.exists(test_data_dir):
        current_test_files = set(os.listdir(test_data_dir))
    else:
        os.makedirs(test_data_dir, mode=0o755)
    gargleblaster_data_mod_path = gargleblaster_test_data_mod.__path__[0]
    gargleblaster_data_files = set([s for s
                              in os.listdir(gargleblaster_data_mod_path)
                              if (not s.startswith('__init__')
                              and not s.startswith('__pycache__'))
                              ])
    gargleblaster_data_to_copy = gargleblaster_data_files - current_test_files
    if gargleblaster_data_to_copy:
        for p in gargleblaster_data_to_copy:
            src = os.path.join(gargleblaster_data_mod_path, p)
            # NOTE: unlike the docs above, test data is deliberately NOT
            # overwritten -- only names not already present are copied, so a
            # user's edits to a test file survive.  The isdir() branch is here
            # because shutil.copy() raises IsADirectoryError on a directory;
            # gargleblaster/test/data currently holds a single file, so this
            # is guarding against a future addition rather than a live bug.
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(test_data_dir, p),
                                dirs_exist_ok=True)
            else:
                shutil.copy(src, test_data_dir)
    # [5] add application-specific (in this case, Gargleblaster-specific)
    # reference data to the pangalactic reference data (p.core.refdata)
    # NOTE: "data.data" is empty at present -- all Data Element Definitions
    # now live in p.core.refdata (see gargleblaster/data.py) -- so this
    # normally adds nothing.  It is kept as the extension point for
    # app-specific reference data, which is what data.py is for, but it is
    # now guarded: an unconditional "+=" on a module-level list would append
    # a second copy of everything if main() were ever called twice in one
    # process (e.g. from a test harness).
    if data.data:
        refdata.core += data.data
    # output logging to console if DEBUG is True
    console = DEBUG
    base_name = app_config['app_base_name']
    run(app_home=app_home_dir, app_base_name=base_name,
        app_version=app_version, release_mode=release_mode, splash_image=None,
        debug=DEBUG, console=console, auth_method=args.auth,
        key_file_name=args.key, use_tls=TLS)

if __name__ == '__main__':
    main()

