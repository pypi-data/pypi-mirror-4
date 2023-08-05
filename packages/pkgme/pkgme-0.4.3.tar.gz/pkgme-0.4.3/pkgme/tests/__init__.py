import unittest

# This test_suite() is not used for the normal 'python setup.py test' run,
# because that command has its own test discovery rules when test_suite points
# to a directory.  However subunit apparently isn't hooked up to that and uses
# the following to discover the tests.
def test_suite():
    module_names = [
        'pkgme.tests.test_api',
        'pkgme.tests.test_backend',
        'pkgme.tests.test_debuild',
        'pkgme.tests.test_distutils_command',
        'pkgme.tests.test_info_elements',
        'pkgme.tests.test_main',
        'pkgme.tests.test_package_files',
        'pkgme.tests.test_project_info',
        'pkgme.tests.test_python_backend',
        'pkgme.tests.test_run_script',
        'pkgme.tests.test_script',
        'pkgme.tests.test_template_file',
        'pkgme.tests.test_testing',
        'pkgme.tests.test_trace',
        'pkgme.tests.test_upload',
        'pkgme.tests.test_vala_backend',
        'pkgme.tests.test_write',
        ]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite
