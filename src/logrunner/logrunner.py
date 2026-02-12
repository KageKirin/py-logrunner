## logrunner

# namespace: logrunner

import sys
import io
import selectors
import subprocess


def run(
    args,
    *,
    stdin=None,
    cwd=None,
    check=False,
    encoding=None,
    errors=None,
    text=None,
    env=None,
    **other_popen_kwargs,
):
    """Run a command and capture its output.

    This function is a wrapper around subprocess.Popen that captures the
    standard output and standard error of the command, and returns them as
    strings. It also allows you to specify various options for how the command
    is run.

    Args:
        args: The command to run, as a list of strings or a single string.
        stdin: The standard input to pass to the command. Can be a string or
            bytes, or a file-like object.
        cwd: The working directory to run the command in.
        check: If True, raise a CalledProcessError if the command exits with a
            non-zero status.
        encoding: The encoding to use for decoding the output. If None, the
            default system encoding is used.
        errors: The error handling strategy to use when decoding the output.
            Can be 'strict', 'ignore', 'replace', or 'backslashreplace'.
        text: If True, decode the output as text using the specified encoding.
            If False, return the output as bytes. If None, the behavior is
            determined by the presence of an encoding argument.
        env: A dictionary of environment variables to set for the command.
        other_popen_kwargs: Additional keyword arguments to pass to subprocess.Popen.

    Returns:
        A tuple (command exit code, stdout, stderr) containing the captured standard output and
        standard error of the command.

    Raises:
        CalledProcessError: If check is True and the command exits with a non-zero status.
    """
    if text is None:
        text = encoding is not None

    if stdin is not None:
        if isinstance(stdin, str):
            stdin = stdin.encode(encoding or sys.getdefaultencoding())
        if isinstance(stdin, bytes):
            stdin = io.BytesIO(stdin)

    popen_kwargs = {
        "stdin": subprocess.PIPE if stdin is not None else None,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "cwd": cwd,
        "env": env,
        **other_popen_kwargs,
    }

    with subprocess.Popen(args, **popen_kwargs) as process:
        selector = selectors.DefaultSelector()

        if process.stdout:
            selector.register(process.stdout, selectors.EVENT_READ)
        if process.stderr:
            selector.register(process.stderr, selectors.EVENT_READ)

        stdout_chunks = []
        stderr_chunks = []

        if stdin is not None:
            stdin_data = stdin.read()
            process.stdin.write(stdin_data)
            process.stdin.close()

        while True:
            for key, _ in selector.select():
                data = key.fileobj.read1(4096)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                if key.fileobj is process.stdout:
                    stdout_chunks.append(data)
                elif key.fileobj is process.stderr:
                    stderr_chunks.append(data)

            if not selector.get_map():
                break

        process.wait()

    stdout = b"".join(stdout_chunks)
    stderr = b"".join(stderr_chunks)

    if text:
        stdout = stdout.decode(encoding or sys.getdefaultencoding(), errors or "strict")
        stderr = stderr.decode(encoding or sys.getdefaultencoding(), errors or "strict")

    if check and process.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=args,
            output=stdout,
            stderr=stderr,
        )

    return process.returncode, stdout, stderr
