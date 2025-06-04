#!/usr/bin/env python
"""
Marvin gui application
"""
import argparse, os, shutil, sys

import marvin
from marvin import __version__ as app_version
from marvin import data
from marvin.test import data as marvin_test_data_mod


def main():
    from pangalactic.core import config, refdata, state
    from pangalactic.node.pangalaxian import run
    # NOTE: pangalactic.core.test[data|vault] and pangalactic.core.ontology
    # need to be imported here so that if we are running the "pyinstaller"
    # installed version of marvin, the data files in those modules can be
    # accessed.
    import pangalactic.core.ontology
    import pangalactic.core.test.data
    import pangalactic.core.test.vault
    app_config = {}
    app_config['app_base_name'] = 'Marvin'
    release_mode = "dev"
    # config:  localized settings; user can edit
    # default configuration:
    if release_mode == 'dev':
        app_config['app_name'] = 'Marvin_dev'
        # dev host
        app_config['host'] = 'marvin.pangalactic.us'
        app_config['port'] = 443
    elif release_mode == 'test':
        app_config['app_name'] = 'Marvin_test'
        # dev host
        app_config['host'] = 'marvin.pangalactic.us'
        app_config['port'] = 443
    else:
        app_config['app_name'] = 'Marvin'
        # production host
        app_config['host'] = 'marvin.pangalactic.us'
        app_config['port'] = 443
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
    args = parser.parse_args()
    # use True for DEBUG default setting (SCW 2018-12-23) ...
    DEBUG = config.get('debug', True) or args.debug
    # use True for TEST to load test data (SCW 2025-01-19) ...
    TEST = config.get('test', False) or args.test
    # use tls unless testing in a non-secure env
    TLS = config.get('tls', True)
    if args.unencrypted:
        # cmd line arg overrides config
        TLS = False
    # create a marvin home directory in the user's home dir
    app_home_dir = ''
    if sys.platform == 'win32':
        user_home = os.path.join(os.environ.get('USERPROFILE'))
        if os.path.exists(user_home):
            if TEST:
                # if TEST mode, make home dir 'marvin_home_test'
                app_home_dir = os.path.join(user_home, 'marvin_home_test')
            else:
                # for dev release, make home dir 'marvin_home_dev'
                # for production release, make home dir 'marvin_home'
                app_home_dir = os.path.join(user_home, 'marvin_home_dev')
    else:
        # Linux or OSX
        user_home = os.environ.get('HOME')
        if user_home:
            if TEST:
                # if TEST mode, make home dir 'marvin_home_test'
                app_home_dir = os.path.join(user_home, 'marvin_home_test')
            else:
                # for dev release, make home dir 'marvin_home_dev'
                # for production release, make home dir 'marvin_home'
                app_home_dir = os.path.join(user_home, 'marvin_home_dev')
    # if all else fails, create 'marvin_home' inside the current directory --
    # not desirable because 'marvin_home' holds user data that needs to
    # persist when a new version of the client is "installed", which typically
    # destroys the current directory.  TODO:  generate warnings if this option
    # is used.
    if not app_home_dir:
        app_home_dir = os.path.join(os.getcwd(), 'marvin_home_dev')
    if not os.path.exists(app_home_dir):
        os.makedirs(app_home_dir, mode=0o755)
    if not os.path.exists(app_home_dir):
        os.makedirs(app_home_dir)
    # update empty 'config' with app_config ... anything in this config can be
    # overridden by user edits to the config file (loaded by Pangalaxian)
    config.update(app_config)
    ##########################################################################
    # The following steps [1]-[7] copy files into known locations within the
    # "marvin_home"/"marvin_home_dev" directory -- a bit messy, but it works
    ##########################################################################
    # [1] create a "vault" directory in app_home
    vault_dir = os.path.join(app_home_dir, 'vault')
    if not os.path.exists(vault_dir):
        os.makedirs(vault_dir, mode=0o755)
    # [2] copy doc files from marvin_doc_path** into the home directory
    #     ** NOTE: marvin_doc_path will only exist if marvin has been
    #     installed
    #     (a) as a conda package or
    #     (b) as a pyinstaller dist
    #     ... i.e., it is not part of the marvin python package but is copied
    #     into the marvin module by running setup.py, conda, or pyinstaller)
    marvin_mod_path = marvin.__path__[0]
    marvin_doc_path = os.path.join(marvin_mod_path, 'doc')
    doc_dir = os.path.join(app_home_dir, 'docs')
    if os.path.exists(marvin_doc_path):
        if os.path.exists(doc_dir):
            current_doc_files = set(os.listdir(doc_dir))
            marvin_doc_files = set([s for s in os.listdir(marvin_doc_path)
                              if (not s.startswith('__init__')
                              and not s.startswith('__pycache__'))
                              ])
            docs_to_copy = marvin_doc_files - current_doc_files
            for d in docs_to_copy:
                shutil.copy(os.path.join(marvin_doc_path, d), doc_dir)
        else:
            # if 'docs' dir does not exist in marvin_home, the entire doc tree
            # is copied over to create it (e.g., if home/doc is removed, it
            # will be "refreshed" ... a possible way to update the distributed
            # docs ...)
            shutil.copytree(marvin_doc_path, doc_dir)
    # [3] if we are running on Windows and pyinstaller installed us, there will
    #     be a 'casroot' directory that contains files needed by pythonocc --
    #     copy them to home and set "CASROOT" env var ...
    if sys.platform == 'win32':
        casroot_path = os.path.join(marvin_mod_path, 'casroot')
        casroot_home = os.path.join(app_home_dir, 'casroot')
        if os.path.exists(casroot_path):
            # copy all casroot files to home dir at startup
            if os.path.exists(casroot_home):
                # if casroot_home already exists, remove it so it can be
                # recreated
                shutil.rmtree(casroot_home, ignore_errors=True)
            shutil.copytree(casroot_path, casroot_home)
            os.environ['CASROOT'] = casroot_home
    # [4] copy test data files from test/data into the "test_data" directory
    test_data_dir = os.path.join(app_home_dir, 'test_data')
    current_test_files = set()
    if os.path.exists(test_data_dir):
        current_test_files = set(os.listdir(test_data_dir))
    else:
        os.makedirs(test_data_dir, mode=0o755)
    marvin_data_mod_path = marvin_test_data_mod.__path__[0]
    marvin_data_files = set([s for s in os.listdir(marvin_data_mod_path)
                              if (not s.startswith('__init__')
                              and not s.startswith('__pycache__'))
                              ])
    marvin_data_to_copy = marvin_data_files - current_test_files
    if marvin_data_to_copy:
        for p in marvin_data_to_copy:
            shutil.copy(os.path.join(marvin_data_mod_path, p), test_data_dir)
    # [6] add application-specific (in this case, Marvin-specific) reference
    # and test data to the PanGalactic reference data (p.core.refdata)
    refdata.core += data.data
    # output logging to console if either TEST or DEBUG is True
    console = TEST or DEBUG
    base_name = app_config['app_base_name']
    run(app_home=app_home_dir, app_base_name=base_name,
        app_version=app_version, release_mode=release_mode, splash_image=None,
        debug=DEBUG, console=console, auth_method=args.auth, use_tls=TLS)

if __name__ == '__main__':
    main()

