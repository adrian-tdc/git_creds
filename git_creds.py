import subprocess
import logging
import os

'''
git_creds.py

Code to compare the github credentials that are currently configured with the
local settings (if in a git repository) or global settings (if outside a git
repository) - the aim here is to flag if these are different as this could
result in you committing changes with the wrong user.

'''

#     Ver    Author          Date       Comments
#     ===    =============== ========== =======================================
ver = 0.1  # ajpowell        2022-12-27 Initial code
ver = 0.2  # ajpowell        2023-01-03 Minor output changes

# Initialise logging module
logging.root.handlers = []
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
    # level=logging.DEBUG
    )


def run_command(command, ignore_lines):
    # logging.debug('--------------------')
    # logging.debug('{} - {}'.format(command[0], command[1]))

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)

    output_stdout = []
    output_stderr = []

    # Loop until command finished...
    while True:
        output_lines = process.stdout.readline()
        line = output_lines.strip()
        if line:
            logging.debug('stdout: ' + line)
            output_stdout.append(line)

        error_lines = process.stderr.readline()
        line = error_lines.strip()
        if line:
            logging.debug('stderr: ' + line)
            output_stderr.append(line)

        # Check for a return code i.e. command complete
        return_code = process.poll()
        if return_code is not None:
            logging.debug('>>> RETURN CODE: {}'.format(return_code))
            break

    return (return_code, output_stdout, output_stderr)


def main():
    # Are we within a git repository?
    cwd = os.getcwd()

    logging.info('Current directory: {}'.format(cwd))

    settings_type = ''

    if os.path.exists('.git'):
        logging.info('This is a git repository - these are local settings.')
        settings_type = 'local '
    else:
        logging.info('This is *not* a git repository - these are global settings.')
        settings_type = 'global'

    # ssh user details
    command = ['ssh', '-T', 'git@github.com']
    retcode, stdout, stderr = run_command(command, '')
    # Parse output
    logging.info('==========')
    # for line in stderr:
    #     logging.info(line)
    exclamation = stderr[0][3:].find('!')
    github_username = stderr[0][3:(exclamation + 3)]
    logging.info('Username reported by github:       {}'.format(github_username))

    # git config user.name
    command = ['git', 'config', 'user.name']
    retcode, stdout, stderr = run_command(command, '')
    git_username = stdout[0]
    logging.info('Username reported by git ({}): {}'.format(settings_type, git_username))

    # git config user.email
    command = ['git', 'config', 'user.email']
    retcode, stdout, stderr = run_command(command, '')
    git_useremail = stdout[0]
    logging.info('email reported by git ({}):    {}'.format(settings_type, git_useremail))

    logging.info('')

    if github_username == git_username:
        logging.info('Settings look good!')
    else:
        logging.info('You will not be commiting as the same user in github!')
        logging.info('')
        logging.info('Change the github details by checking the ssh keys.')
        logging.info('')
        logging.info('Change the local details with:')
        logging.info('   git config user.name <username>')
        logging.info('   git config user.email <email>')


if __name__ == '__main__':
    logging.info('')
    logging.info('{} v{}'.format(os.path.basename(__file__), ver))
    logging.info('')
    main()
