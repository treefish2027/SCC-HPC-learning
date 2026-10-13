import os
import pathlib
import subprocess
import tempfile
from test_public import encode, decode, reference

ROOT = pathlib.Path(__file__).resolve().parent
QUERY = (1000, 2000, 100, 3)

# Uneven length; alternating groups of hits and misses.
mixed = [
    (1500, i, 100 if (i // 17) % 2 == 0 else 99, i * 19, 3)
    for i in range(259)
]

cases = {
    "empty": [],
    "single": [(1000, 7, 100, 123, 3)],
    "fewer_records_than_threads": [
        (1500, 3, 100, 33, 3),
        (1500, 2, 99, 22, 3),
        (1500, 1, 100, 11, 3),
    ],
    "uneven_blocks": mixed,
    "duplicates_and_reverse_order": [
        (1500, i % 7, 100, i % 5, 3)
        for i in range(258, -1, -1)
    ],
}

checks = 0
with tempfile.TemporaryDirectory() as temp:
    temp = pathlib.Path(temp)
    for threads in (1, 2, 3, 8):
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(threads)
        env["OMP_DYNAMIC"] = "FALSE"

        for name, rows in cases.items():
            src = temp / "input.bin"
            original = encode(rows)
            src.write_bytes(original)
            expected = reference(rows, QUERY)

            for executable in ("log_filter_serial", "log_filter_openmp"):
                dst = temp / "output.bin"
                if dst.exists():
                    dst.unlink()

                result = subprocess.run(
                    [str(ROOT / executable),
                     "--input", str(src), "--output", str(dst),
                     "--repeats", "1",
                     "--begin", "1000", "--end", "2000",
                     "--min-latency", "100", "--flags", "3"],
                    env=env, capture_output=True, text=True, timeout=30,
                )
                label = f"{executable}, threads={threads}, case={name}"
                assert result.returncode == 0, (
                    label + "\n" + result.stdout + result.stderr
                )
                assert decode(dst.read_bytes()) == expected, label
                assert src.read_bytes() == original, label + ": input changed"
                checks += 1

            print(f"PASS threads={threads} case={name}")

print(f"OK: {checks} program checks passed")
