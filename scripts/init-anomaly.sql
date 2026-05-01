-- Enable vector extension (already in init-db.sql but good for completeness)
CREATE EXTENSION IF NOT EXISTS vector;

-- Metric Samples: Raw time-series data for baseline modeling
CREATE TABLE IF NOT EXISTS metric_samples (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    account_id TEXT NOT NULL,
    region TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    resource_id TEXT,
    value DOUBLE PRECISION NOT NULL
);

-- Index for fast time-range queries
CREATE INDEX IF NOT EXISTS idx_metrics_time ON metric_samples (time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_lookup ON metric_samples (metric_name, account_id, time DESC);

-- Baselines: Calculated hourly statistical models
CREATE TABLE IF NOT EXISTS baselines (
    metric_key TEXT NOT NULL,      -- e.g. "account_id:region:metric_name:resource_id"
    hour_bucket SMALLINT NOT NULL,  -- 0-23
    day_type TEXT NOT NULL,         -- 'weekday' or 'weekend'
    ewma DOUBLE PRECISION,
    ewma_var DOUBLE PRECISION,
    sample_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (metric_key, hour_bucket, day_type)
);

-- Anomaly Events: Historical record of detected anomalies
CREATE TABLE IF NOT EXISTS anomaly_events (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    anomaly_type TEXT NOT NULL,     -- 'cost_spike', 'iam_drift', 'gpu_abuse', etc.
    resource_id TEXT,
    account_id TEXT,
    metric_name TEXT,
    observed_value DOUBLE PRECISION,
    expected_value DOUBLE PRECISION,
    z_score DOUBLE PRECISION,
    composite_score DOUBLE PRECISION,
    tier TEXT,                      -- 'T1', 'T2', 'T3'
    status TEXT DEFAULT 'detected',  -- 'detected', 'alerted', 'remediated', 'ignored'
    feedback TEXT                   -- 'true_positive', 'false_positive'
);

-- Index for anomaly lookup
CREATE INDEX IF NOT EXISTS idx_anomalies_time ON anomaly_events (detected_at DESC);
