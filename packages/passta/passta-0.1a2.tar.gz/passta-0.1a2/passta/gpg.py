from subprocess import Popen, PIPE


class GpgError(Exception): pass


def gpg(gpg_args, stdin):
    cmd = ['gpg', '-q', '--batch', '--no-tty']
    if gpg_args:
        cmd.extend(gpg_args)
    p = Popen(cmd, stdin=PIPE, stdout=PIPE)
    stdout, _ = p.communicate(stdin)
    status = p.wait()
    if status:
        raise GpgError('gpg exited with status {}'.format(status))
    return stdout


def decrypt(encrypted):
    return gpg(['-d'], encrypted)


def encrypt(decrypted):
    return gpg(['-e', '--armor', '--default-recipient-self'], decrypted)
