# Tests

Self-contained test scripts, organised by language:

```
test/
├── python/
│   ├── seed/          # DB seeding script
│   │   ├── seed.py
│   │   └── seeds.yaml
│   └── my-test/       # Another test
│       └── test.py
```

Each test directory is independent and executed by the `run-tests` tool.
Auto-detected entry points (in order): `seed.py`, `test.py`, `main.py`, `run.py`.
