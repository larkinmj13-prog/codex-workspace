"""Provider-backed factual evidence layer for Stock God Evidence Engine v6.

Connects normalized read-only provider envelopes to the existing deterministic
engine by producing fact-only snapshots and engine inputs. It records what the
providers returned and the freshness of that data; it does not score, rate,
rank, compute technical levels, infer buy/sell intent, or fabricate missing
values. Unknown facts are recorded as ``missing`` so the deterministic engine
applies its own conservative defaults.
"""
