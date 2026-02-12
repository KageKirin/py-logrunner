## logrunner

# namespace: logrunner

import io
import sys
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

    stdoutbuf = io.StringIO()
    stderrbuf = io.StringIO()

    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,  # STDOUT to pipe STDERR into STDOUT for simultaneous capture
        "bufsize": 1,  # bufsize = 1 means output is line buffered
        "universal_newlines": True,  # required for line buffering
        ## forwarding the remaining params
        "stdin": stdin,
        "cwd": cwd,
        # timeout=timeout,
        "errors": errors,
        "text": text,
        "env": env,
        **other_popen_kwargs,
    }

    # Start subprocess
    process = subprocess.Popen(args, **kwargs)

    # Callback function for process STDOUT
    def handle_stdout(stream, mask):
        # NOTE: Because the process' output is line buffered, there's only ever one line to read when this function is called
        line = stream.readline()
        stdoutbuf.write(line)
        sys.stdout.write(line)

    # Callback function for process STDERR
    def handle_stderr(stream, mask):
        # NOTE: Because the process' output is line buffered, there's only ever one line to read when this function is called
        line = stream.readline()
        stderrbuf.write(line)
        sys.stderr.write(line)

    # Register callback for an "available for read" event from subprocess' stdout stream
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, handle_stdout)
    selector.register(process.stderr, selectors.EVENT_READ, handle_stderr)

    # Loop until subprocess is terminated
    while process.poll() is None:
        # Wait for events and handle them with their registered callbacks
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

    # Get process return code
    returncode = process.wait()
    selector.close()

    # Store buffered output
    stdoutput = stdoutbuf.getvalue()
    stdoutbuf.close()
    stderrput = stderrbuf.getvalue()
    stderrbuf.close()

    if check and returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=returncode,
            cmd=" ".join(args),
            output=stdoutput,
            stderr=stderrput,
        )

    return (returncode, stdoutput, stderrput)
