from math import ceil


class Statistics:

    def __init__(self, block):
        self.block = block
        self.num = 0
        self.mean_cpu = 0
        self.var_cpu = 0
        self.mean_wall = 0
        self.var_wall = 0
        self.perc_cpu = None
        self.perc_wall = None
        self.perc_times = None
        self.baseline_fraction = None
        self.last_timestamp = None
        self.mean_delta = 0
        self.delta_num = 0


class ExecutionStats:

    def __init__(self):
        self.samples = {}

    def add(self, block, cpu, wall, timestamp):
        # weird wall/cpu behavior when suspending the process
        if wall < 0:
            wall = 1
        if cpu < 0:
            cpu = wall

        if cpu == 0:
            cpu = 0.0001
        if wall == 0:
            wall = 0.0001

        if not block in self.samples:
            self.samples[block] = Statistics(block)

        s = self.samples[block]

        # TODO: set parameter
        WINDOW = 100
        N = min(s.num, WINDOW)

        s.mean_cpu = (s.mean_cpu * N + cpu) / (N + 1)
        s.var_cpu = (s.var_cpu * N + (cpu - s.mean_cpu) ** 2) / (N + 1)
        s.mean_wall = (s.mean_wall * N + wall) / (N + 1)
        s.var_wall = (s.var_wall * N + (wall - s.mean_wall) ** 2) / (N + 1)
        s.num += 1

        if isinstance(timestamp, float):
            if s.last_timestamp is not None:
                delta = timestamp - s.last_timestamp
                # when the block is a model, it could be called multiple times
                if delta > 0:
                    N = s.delta_num
                    s.mean_delta = (s.mean_delta * N + delta) / (N + 1)
                    s.delta_num += 1
                    # print "%s %d mean %d" % 
                    # (s.block, delta * 1000, 1000 * s.mean_delta)

        s.last_timestamp = timestamp

    def print_info(self):
        samples = list(self.samples.values())
        write_stats(samples)


def write_stats(samples):
    for s in samples:
        assert isinstance(s, Statistics)

    # get the block that executed fewest times and use it as a baseline
    baseline = min(samples, key=lambda s: s.num)

    # update percentage
    total_cpu = sum([s.mean_cpu * s.num for s in samples])
    total_wall = sum([s.mean_wall * s.num for s in samples])
    total_times = sum([s.num for s in samples])
    for s in samples:
        s.perc_cpu = s.mean_cpu * s.num / total_cpu
        s.perc_wall = s.mean_wall * s.num / total_wall
        s.perc_times = s.num * 1.0 / total_times
        s.baseline_fraction = s.num * 1.0 / baseline.num

    # sort by percentage
    alls = sorted(list(samples), key=lambda x: (-x.perc_wall))
    min_perc = 3
    print('--- Statistics (ignoring < %d%%) baseline: %d iterations of %s' %
          (min_perc, baseline.num, baseline.block))
    for s in alls:
        perc_cpu = ceil(s.perc_cpu * 100)
        perc_wall = ceil(s.perc_wall * 100)
        if (s != baseline and
             (perc_cpu < min_perc) and
             (perc_wall < min_perc)):
            continue
        perc_times = ceil(s.perc_times * 100)

        # jitter_cpu = ceil(100 * (sqrt(s.var_cpu) * 2 / s.mean_cpu))
        # jitter_wall = ceil(100 * (sqrt(s.var_wall) * 2 / s.mean_wall))

        if s.mean_cpu < 0.7 * s.mean_wall:
            comment = 'IO '
        else:
            comment = '   '
        #print ''.join([
        #'- cpu: %dms (+-%d%%) %02d%% of total; ' % 
        # (1000 * s.mean_cpu, jitter_cpu, perc_cpu),
        #'wall: %dms (+-%d%%) %02d%% of total; ' % 
        #(1000 * s.mean_wall, jitter_wall, perc_wall),
        #'exec: %02d%% of total' % perc_times])

        if s.mean_delta > 0:
            fps = 1.0 / s.mean_delta
            stats = '%3.1f fps' % fps
        else:
            stats = ' ' * len('%3.1f fps' % 0)

        name = str(s.block)
        if len(name) > 35:
            name = name[:35]
        print(''.join([
            ' cpu %4dms %2d%%| ' % (1000 * s.mean_cpu, perc_cpu),
            'wall %4dms %2d%%| ' % (1000 * s.mean_wall, perc_wall),
            'exec %2d%% %3d (%3.1fx) %s| %s ' % (perc_times,
                                             s.num,
                                             s.baseline_fraction,
                                                      stats, comment),
                                                      name]))


