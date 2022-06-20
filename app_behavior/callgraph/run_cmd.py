import subprocess


def run_jar(time_out, cmd, output):
    print(' '.join(cmd))
    if time_out == 0:
        return subprocess.run(cmd, stdout=output, stderr=output)
    else:
        try:
            return subprocess.run(cmd, stdout=output, stderr=output, timeout=time_out)
        except subprocess.TimeoutExpired:
            return -50
