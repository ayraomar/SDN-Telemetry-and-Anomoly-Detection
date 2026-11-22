class EWMADetector:
    """EWMA + z-score on one value (packets/sec)."""
    def __init__(self, alpha=0.2, z_thresh=4.0, warmup=10, min_pps=200):
        self.alpha, self.z_thresh, self.warmup, self.min_pps = alpha, z_thresh, warmup, min_pps
        self.mean, self.var, self.n = 0.0, 0.0, 0

    def _learn(self, x):
        if self.n == 0:
            self.mean = x
        else:
            d = x - self.mean
            self.mean += self.alpha * d
            self.var = (1 - self.alpha) * (self.var + self.alpha * d * d)
        self.n += 1

    def update(self, x):
        if self.n < self.warmup:
            self._learn(x)
            return 0.0, False
        std = max(self.var ** 0.5, 0.1 * self.mean, 5.0)  # floor avoids divide-by-0
        z = (x - self.mean) / std
        alarm = z > self.z_thresh and x > self.min_pps
        if not alarm:
            self._learn(x)  # never learn attack traffic as "normal"
        return z, alarm
