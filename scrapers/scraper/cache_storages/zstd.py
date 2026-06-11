from __future__ import annotations

import logging
import pickle
import random
import sqlite3
import statistics
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import TYPE_CHECKING, Any

import zstandard
from scrapy.http import Headers, Response
from scrapy.responsetypes import responsetypes
from scrapy.utils.project import data_path
from scrapy.utils.request import RequestFingerprinter

if TYPE_CHECKING:
    from scrapy.http.request import Request
    from scrapy.settings import BaseSettings
    from scrapy.spiders import Spider

logger = logging.getLogger(__name__)

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS metadata (
    key   TEXT PRIMARY KEY,
    value BLOB
);

CREATE TABLE IF NOT EXISTS responses (
    fingerprint      TEXT PRIMARY KEY,
    url              TEXT NOT NULL,
    status           INTEGER NOT NULL,
    headers_blob     BLOB NOT NULL,
    body             BLOB NOT NULL,
    timestamp        REAL NOT NULL,
    compressed       INTEGER NOT NULL DEFAULT 0
);
"""

_PRAGMAS = [
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA temp_store=MEMORY",
    "PRAGMA mmap_size=30000000000",
]


@dataclass
class ZSTDCodecs:
    # fmt: off
    compressor:    zstandard.ZstdCompressor
    decompressor:  zstandard.ZstdDecompressor
    zstd_dict:     zstandard.ZstdCompressionDict
    # fmt: on

    @classmethod
    def load_from_stored(cls, db: sqlite3.Connection, level: int = 6, key: str | None = None) -> ZSTDCodecs | None:
        key = f"zstd_dict-{key}" if key else "zstd_dict"
        row = db.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        if row is not None:
            return ZSTDCodecs.make_from_dict_bytes(row[0], level)
        else:
            return None

    def store(self, db: sqlite3.Connection, key: str) -> None:
        key = f"zstd_dict-{key}" if key else "zstd_dict"
        db.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (
                key,
                self.serialized_dict,
            ),
        )
        db.commit()

    @classmethod
    def make_from_dict_bytes(cls, dict_bytes: bytes, level: int = 6) -> ZSTDCodecs:
        zstd_dict = zstandard.ZstdCompressionDict(dict_bytes)
        zstd_dict.precompute_compress(level=level)
        return cls.make_from_dict(zstd_dict, level)

    @classmethod
    def make_from_dict(cls, zstd_dict: zstandard.ZstdCompressionDict, level: int = 6) -> ZSTDCodecs:
        compressor = zstandard.ZstdCompressor(level=level, dict_data=zstd_dict)
        decompressor = zstandard.ZstdDecompressor(dict_data=zstd_dict)
        return ZSTDCodecs(
            compressor=compressor,
            decompressor=decompressor,
            zstd_dict=zstd_dict,
        )

    @classmethod
    def autotune(cls, samples: list[bytes], level: int = 6):
        # --- Shuffle to avoid biased split ---
        sizes = [len(body) for body in samples]
        print(
            f"Number of samples: {len(sizes)}, median: {statistics.median(sizes)/1024} kb, mean: {statistics.mean(sizes)/1024} kb, min: {min(sizes)/1024} kb, max: {max(sizes)/1024} kb"
        )

        samples = samples.copy()
        random.shuffle(samples)

        split_idx = int(len(samples) * 0.9)
        train_samples, test_samples = samples[:split_idx], samples[split_idx:]

        results = []

        for size_kb in [1, *[2**i for i in range(10)]]:
            for k in [2**i for i in range(4, 11)]:
                dict_size = size_kb * 1024

                try:
                    codecs = cls.__make_from_sample(train_samples, level, dict_size, k)

                    ratios = []
                    for sample in test_samples:
                        compressed = codecs.compress(sample)
                        ratios.append(len(compressed) / len(sample))

                    avg_ratio = statistics.mean(ratios)
                    results.append((size_kb, avg_ratio, codecs))

                    print(
                        f"Tested {size_kb:3d} KB → ratio {avg_ratio:.4f}, k={codecs.zstd_dict.k}, d={codecs.zstd_dict.d}"
                    )

                except Exception as e:
                    print(f"Skipped {size_kb} KB → {e}")

        # --- Sort by best compression (smaller ratio = better) ---
        tolerance = 0.01  # 2 digits after decimal
        results.sort(key=lambda x: (round(x[1] / tolerance) * tolerance, x[0]))

        best_size, best_ratio, best_codecs = results[0]

        print("\n=== TOP 10 RESULTS ===")
        print("Size (KB) | Avg Ratio")
        print("----------------------")
        for size_kb, ratio, _ in results[:10]:
            print(f"{size_kb:9d} | {ratio:.4f}")

        print("\n=== BEST DICTIONARY ===")
        print(f"Size: {best_size} KB")
        print(f"Ratio: {best_ratio:.4f}")
        print(f"k: {best_codecs.zstd_dict.k}")
        print(f"d: {best_codecs.zstd_dict.d}")

        return best_codecs

    @classmethod
    def __make_from_sample(cls, samples: list[bytes], level: int, dict_size: int, k: int) -> ZSTDCodecs:
        zstd_dict = zstandard.train_dictionary(
            dict_size, samples, steps=10, accel=10, split_point=0.8, notifications=0, d=6, k=k
        )
        zstd_dict.precompute_compress(level=level)
        return cls.make_from_dict(zstd_dict, level)

    @classmethod
    def simple_autotune(cls, samples: list[bytes], level: int = 6):
        sizes = [len(body) for body in samples]
        m = statistics.median(sizes)
        dict_size = int(max(1024, min(m * 0.7, 192 * 1024)))
        zstd_dict = zstandard.train_dictionary(dict_size, samples)
        zstd_dict.precompute_compress(level=level)
        return cls.make_from_dict(zstd_dict, level)

    @classmethod
    def make_from_sample(cls, samples: list[bytes], level: int = 6) -> ZSTDCodecs:
        logger.info(f"Training zstd dictionary from {len(samples)} samples")
        now = time()
        codecs = cls.autotune(samples, level)
        # codecs = cls.simple_autotune(samples, level)
        logger.info(f"Dictionary trained in {time() - now:.2f} seconds")
        return codecs

    @property
    def serialized_dict(self) -> bytes:
        return self.zstd_dict.as_bytes()

    def compress(self, data: bytes) -> bytes:
        return self.compressor.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return self.decompressor.decompress(data)


@dataclass
class ZSTDPageCodecs:
    # fmt: off
    body:    ZSTDCodecs
    headers: ZSTDCodecs | None
    # fmt: on

    @classmethod
    def load_from_stored(cls, db: sqlite3.Connection, level: int = 6) -> ZSTDPageCodecs | None:
        body = ZSTDCodecs.load_from_stored(db, level, key="body")
        headers = ZSTDCodecs.load_from_stored(db, level, key="headers")
        if body is None:
            return None
        return cls(body=body, headers=headers)

    def store(self, db: sqlite3.Connection) -> None:
        self.body.store(db, key="body")
        if self.headers:
            self.headers.store(db, key="headers")

    @classmethod
    def make_from_sample(
        cls, body_samples: list[bytes], headers_samples: list[bytes] | None = None, level: int = 6
    ) -> ZSTDPageCodecs:
        body_codecs = ZSTDCodecs.make_from_sample(body_samples, level)
        headers_codecs = None
        if headers_samples:
            headers_codecs = ZSTDCodecs.make_from_sample(headers_samples, level)
        return cls(body=body_codecs, headers=headers_codecs)

    def compress_body(self, data: bytes) -> bytes:
        return self.body.compressor.compress(data)

    def decompress_body(self, data: bytes) -> bytes:
        return self.body.decompressor.decompress(data)

    def compress_headers(self, data: bytes) -> bytes:
        if not self.headers:
            return data
        return self.headers.compressor.compress(data)

    def decompress_headers(self, data: bytes) -> bytes:
        if not self.headers:
            return data
        return self.headers.decompressor.decompress(data)


def _open_db(dbpath: Path) -> sqlite3.Connection:
    """Open a SQLite connection with performance PRAGMAs and schema."""
    dbpath.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(dbpath))
    for pragma in _PRAGMAS:
        db.execute(pragma)
    db.executescript(_SCHEMA)
    return db


# ---------------------------------------------------------------------------
# Partition: pure SQLite (no compression)
# ---------------------------------------------------------------------------


class SqliteCacheStoragePartition:
    """Standalone SQLite cache partition without compression."""

    def __init__(
        self,
        cachedir: str,
        fingerprinter: RequestFingerprinter,
        spider_dir: str,
        partition: str,
        commit_interval: int,
        expiration_secs: int,
    ):
        self.partition = partition
        self.fingerprinter = fingerprinter
        self.commit_interval = commit_interval
        self.expiration_secs = expiration_secs

        dbpath = Path(cachedir) / spider_dir / f"{partition}.sqlite"
        self.db = _open_db(dbpath)
        self.pending_writes: int = 0

    # -- public interface ---------------------------------------------------

    def store_response(self, request: Request, response: Response) -> None:
        key, headers_blob, body = self._serialize(request, response)
        self._store_row(key, response.url, response.status, headers_blob, body, compressed=0)

    def retrieve_response(self, request: Request) -> Response | None:
        row = self._fetch_row(request)
        if row is None:
            return None
        url, status, headers_blob, body, _ts, is_compressed = row
        if is_compressed:
            logger.warning("Compressed row found but no decompressor available")
            return None
        return self._build_response(url, status, headers_blob, body)

    # -- internal helpers (used by zstd wrapper via composition) -------------

    def _serialize(self, request: Request, response: Response) -> tuple[str, bytes, bytes]:
        """Fingerprint + pickle headers -> (key, headers_blob, body)."""
        key = self.fingerprinter.fingerprint(request).hex()
        headers_blob = pickle.dumps(
            {
                "request_headers": dict(request.headers),
                "response_headers": dict(response.headers),
                "request_body": request.body,
            },
            protocol=4,
        )
        return key, headers_blob, response.body

    def _store_row(
        self,
        key: str,
        url: str,
        status: int,
        headers_blob: bytes,
        body: bytes,
        compressed: int,
    ) -> None:
        """INSERT row + batch commit logic."""
        now = time()
        self.db.execute(
            """INSERT OR REPLACE INTO responses
               (fingerprint, url, status, headers_blob, body, timestamp, compressed)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (key, url, status, headers_blob, body, now, compressed),
        )
        self.pending_writes += 1
        if self.pending_writes >= self.commit_interval:
            self.db.commit()
            self.pending_writes = 0

    def _fetch_row(self, request: Request) -> tuple[Any, ...] | None:
        """Fingerprint -> SELECT -> raw row or None (includes expiration check)."""
        key = self.fingerprinter.fingerprint(request).hex()
        row = self.db.execute(
            """SELECT url, status, headers_blob, body, timestamp, compressed
               FROM responses WHERE fingerprint = ?""",
            (key,),
        ).fetchone()
        if row is None:
            return None
        _url, _status, _headers_blob, _body, ts, _compressed = row
        if 0 < self.expiration_secs < time() - ts:
            return None
        return row

    def _build_response(self, url: str, status: int, headers_blob: bytes, body: bytes) -> Response:
        """Unpickle headers + reconstruct Response object."""
        meta: dict[str, Any] = pickle.loads(headers_blob)  # noqa: S301
        response_headers = Headers(meta["response_headers"])
        respcls = responsetypes.from_args(headers=response_headers, url=url, body=body)
        return respcls(url=url, headers=response_headers, status=status, body=body)


# ---------------------------------------------------------------------------
# Partition: zstd-compressed (wraps SqliteCacheStoragePartition)
# ---------------------------------------------------------------------------


class ZstdSqliteCacheStoragePartition:
    """Zstd-compressed cache partition. Composes a SqliteCacheStoragePartition."""

    def __init__(
        self,
        store: SqliteCacheStoragePartition,
        dict_sample_count: int,
        zstd_level: int,
    ):
        self.store = store
        self.dict_sample_count = dict_sample_count
        self.zstd_level = zstd_level

        self.codecs: ZSTDPageCodecs | None = ZSTDPageCodecs.load_from_stored(self.store.db, self.zstd_level)

        if self.codecs is None:
            row = self.store.db.execute("SELECT COUNT(*) FROM responses WHERE compressed = 0").fetchone()
            self.uncompressed_count: int = row[0] if row else 0
        else:
            self.uncompressed_count = 0

    @property
    def db(self) -> sqlite3.Connection:
        return self.store.db

    @property
    def pending_writes(self) -> int:
        return self.store.pending_writes

    @property
    def fingerprinter(self) -> RequestFingerprinter:
        return self.store.fingerprinter

    def store_response(self, request: Request, response: Response) -> None:
        key, headers_blob, body = self.store._serialize(request, response)

        if self.codecs:
            headers_blob = self.codecs.compress_headers(headers_blob)
            body = self.codecs.compress_body(body)
            is_compressed = 1
        else:
            is_compressed = 0

        self.store._store_row(key, response.url, response.status, headers_blob, body, is_compressed)

        if is_compressed == 0:
            self.uncompressed_count += 1
            if self.uncompressed_count >= self.dict_sample_count:
                self._train_and_compress()

    def retrieve_response(self, request: Request) -> Response | None:
        row = self.store._fetch_row(request)
        if row is None:
            return None
        url, status, headers_blob, body, _ts, is_compressed = row

        if is_compressed:
            if self.codecs is None:
                logger.warning("Compressed row found but no dictionary loaded")
                return None
            headers_blob = self.codecs.decompress_headers(headers_blob)
            body = self.codecs.decompress_body(body)

        return self.store._build_response(url, status, headers_blob, body)

    def _train_and_compress(self) -> None:
        """Train a zstd dictionary from uncompressed responses and compress all rows."""
        rows = self.store.db.execute(
            "SELECT fingerprint, headers_blob, body FROM responses WHERE compressed = 0"
        ).fetchall()
        if not rows:
            return

        body_samples = [body for f, header, body in rows if body]
        headers_samples = [header for f, header, body in rows if header]

        logger.info(
            "Training zstd dictionary from %d body samples (%d bytes total)",
            len(body_samples),
            sum(len(s) for s in body_samples),
        )

        self.codecs = ZSTDPageCodecs.make_from_sample(
            body_samples=body_samples, headers_samples=headers_samples, level=self.zstd_level
        )
        self.codecs.store(self.store.db)

        for fingerprint, raw_headers, raw_body in rows:
            compressed_headers = self.codecs.compress_headers(raw_headers)
            compressed_body = self.codecs.compress_body(raw_body)
            self.store.db.execute(
                """UPDATE responses
                   SET headers_blob = ?, body = ?, compressed = 1
                   WHERE fingerprint = ?""",
                (compressed_headers, compressed_body, fingerprint),
            )

        self.store.db.commit()
        self.store.pending_writes = 0
        self.store.db.execute("VACUUM")
        self.uncompressed_count = 0
        logger.info("Dictionary trained and %d rows compressed", len(rows))


# ---------------------------------------------------------------------------
# Outer storage: pure SQLite
# ---------------------------------------------------------------------------


class SqliteCacheStorage:
    """Scrapy cache storage backend using a single SQLite file per partition.

    No compression. Suitable when zstd is not needed or as a lightweight
    alternative. Partitions can be customized via
    ``request.meta['cache_partition_key']``.
    """

    def __init__(self, settings: BaseSettings):
        self.cachedir: str = data_path(settings["HTTPCACHE_DIR"], createdir=True)
        self._partitions: dict[str, SqliteCacheStoragePartition] = {}
        self._fingerprinter: RequestFingerprinter | None = None
        self._settings: BaseSettings = settings

    def open_spider(self, spider: Spider) -> None:
        assert spider.crawler.request_fingerprinter
        self._fingerprinter = spider.crawler.request_fingerprinter
        self._get_partition(spider, spider.name)
        logger.debug(
            "Using sqlite cache storage in %(cachedir)s",
            {"cachedir": self.cachedir},
            extra={"spider": spider},
        )

    def close_spider(self, spider: Spider) -> None:
        for partition in self._partitions.values():
            if partition.pending_writes > 0:
                partition.db.commit()
            partition.db.close()
        self._partitions.clear()

    def _get_partition(self, spider: Spider, partition_key: str) -> SqliteCacheStoragePartition:
        if partition_key not in self._partitions:
            safe_spider_name = "".join(c if c.isalnum() else "_" for c in spider.name).rstrip("_")
            self._partitions[partition_key] = SqliteCacheStoragePartition(
                cachedir=self.cachedir,
                fingerprinter=self._fingerprinter,  # type: ignore[arg-type]
                spider_dir=safe_spider_name,
                partition=partition_key,
                commit_interval=self._settings.getint("HTTPCACHE_ZSTD_CACHE_COMMIT_INTERVAL", 50),
                expiration_secs=self._settings.getint("HTTPCACHE_EXPIRATION_SECS", 0),
            )
        return self._partitions[partition_key]

    def store_response(self, spider: Spider, request: Request, response: Response) -> None:
        partition_key = request.meta.get("cache_partition_key", spider.name)
        partition = self._get_partition(spider, partition_key)
        partition.store_response(request, response)

    def retrieve_response(self, spider: Spider, request: Request) -> Response | None:
        partition_key = request.meta.get("cache_partition_key", spider.name)
        partition = self._get_partition(spider, partition_key)
        return partition.retrieve_response(request)


# ---------------------------------------------------------------------------
# Outer storage: zstd + SQLite
# ---------------------------------------------------------------------------

class ZstdSqliteCacheStorage:
    """Scrapy cache storage backend using SQLite + zstd dictionary compression.

    All cached data is stored in a single SQLite file per partition (default:
    one per spider). After collecting ``ZSTD_DICT_SAMPLE_COUNT`` responses,
    a zstd dictionary is trained from the response bodies and all data is
    compressed.

    Partitions can be customized via ``request.meta['cache_partition_key']``.
    """

    def __init__(self, settings: BaseSettings):
        self.cachedir: str = data_path(settings["HTTPCACHE_DIR"], createdir=True)
        self._partitions: dict[str, ZstdSqliteCacheStoragePartition] = {}
        self._fingerprinter: RequestFingerprinter | None = None
        self._settings: BaseSettings = settings

    def open_spider(self, spider: Spider) -> None:
        assert spider.crawler.request_fingerprinter
        self._fingerprinter = spider.crawler.request_fingerprinter
        self._get_partition(spider, spider.name)
        logger.debug(
            "Using zstd+sqlite cache storage in %(cachedir)s",
            {"cachedir": self.cachedir},
            extra={"spider": spider},
        )

    def close_spider(self, spider: Spider) -> None:
        for partition in self._partitions.values():
            if partition.pending_writes > 0:
                partition.db.commit()
            partition.db.close()
        self._partitions.clear()

    def _get_partition(self, spider: Spider, partition_key: str) -> ZstdSqliteCacheStoragePartition:
        if partition_key not in self._partitions:
            safe_spider_name = "".join(c if c.isalnum() else "_" for c in spider.name).rstrip("_")
            store = SqliteCacheStoragePartition(
                cachedir=self.cachedir,
                fingerprinter=self._fingerprinter,  # type: ignore[arg-type]
                spider_dir=safe_spider_name,
                partition=partition_key,
                commit_interval=self._settings.getint("HTTPCACHE_ZSTD_CACHE_COMMIT_INTERVAL", 50),
                expiration_secs=self._settings.getint("HTTPCACHE_EXPIRATION_SECS", 0),
            )
            self._partitions[partition_key] = ZstdSqliteCacheStoragePartition(
                store=store,
                dict_sample_count=self._settings.getint("HTTPCACHE_ZSTD_DICT_SAMPLE_COUNT", 1000),
                zstd_level=self._settings.getint("HTTPCACHE_ZSTD_COMPRESSION_LEVEL", 6),
            )
        return self._partitions[partition_key]

    def store_response(self, spider: Spider, request: Request, response: Response) -> None:
        partition_key = request.meta.get("cache_partition_key", spider.name)
        partition = self._get_partition(spider, partition_key)
        partition.store_response(request, response)

    def retrieve_response(self, spider: Spider, request: Request) -> Response | None:
        partition_key = request.meta.get("cache_partition_key", spider.name)
        partition = self._get_partition(spider, partition_key)
        return partition.retrieve_response(request)