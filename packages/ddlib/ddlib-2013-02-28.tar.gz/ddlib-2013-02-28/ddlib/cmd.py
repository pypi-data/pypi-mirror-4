
import subprocess
from . import log_debug, log_info, log_error


def bash(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return p.returncode, stdout.decode(), stderr.decode()



def run(host, cmd, suppres_log=0, exit_on_error=1):
	if host != 'local': cmd = 'ssh %s "%s"' % (host, cmd)
	r, stdout, stderr = bash(cmd)
	stdout = stdout.strip()
	stderr = stderr.strip()
	if not suppres_log:
		if r != 0 or stderr:
			log_info('-'*60)
			log_info('HOST: %s CMD: %s' % (host, cmd))
			if r != 0: log_error('!!! return code: %s' % r)
			if stderr:
				log_error('--- stderr:')
				log_error(stderr)

			if stdout:
				log_info('--- stdout:')
				log_info(stdout)

			log_info('-'*60)

	if exit_on_error and r != 0:
		exit(1)

	return stdout