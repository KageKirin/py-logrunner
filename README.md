# Logrunner

`logrunner.run([cmd])` wraps `subprocess.run([cmd])` to allow continuous output as well as capture of stdout and stderr.

This function is intended for usage in CI and other process monitoring applications where
the process outputs need to be written for real-time error tracking
and captured for post-processing text analysis.

## ⚡ Usage

```python
import logrunner

(ret, out, err) = logrunner.run(["echo", "hello"])
# returns (0, "hello", "")

(ret, out, err) = logrunner.run(["ls", "/nonexistentpath"])
# return (1, "", "No such file or directory")
```

## 🔧 Building

```shell
uv build
```

## 🤝 Collaborate with My Project

Please refer to the [collaboration guidelines](./COLLABORATION.md) for details.
