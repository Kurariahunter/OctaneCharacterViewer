"""Default applied boundary byte 0xF8, with explicit activation and stop.

Bounded phase/state model; callback delivery and native metadata are not emulated.
"""
import math
from native_default_clock import f32,DemandClockConsumer

class DefaultCurveTime:
    def __init__(self, lower, upper, *, phase=None, rate1=1., rate2=1., reverse=False):
        values=[lower,upper,rate1,rate2]+([] if phase is None else [phase])
        if not all(math.isfinite(v) for v in values):raise ValueError('Finite values required')
        self.lower,self.upper=f32(lower),f32(upper)
        if self.upper<=self.lower:raise ValueError('Positive float32 range required')
        self.phase=f32(self.lower if phase is None else phase)
        if not self.lower<=self.phase<=self.upper:raise ValueError('Initial phase outside range')
        self.rate1,self.rate2=f32(rate1),f32(rate2)
        self.reverse=bool(reverse)
        self.previous_clock=0.
        self.state_byte63=3
        self.consumer=DemandClockConsumer(self._evaluate)

    def activate(self, inputs):
        if inputs is None:raise ValueError('Publish clock inputs before activation')
        if self.state_byte63&1:self.previous_clock=f32(inputs.seconds)
        self.state_byte63=0
        # Native activation invalidates output even within one publication.
        self.consumer.inputs=None

    def pause(self):
        self.state_byte63=1
        self.consumer.inputs=None

    def _evaluate(self, inputs):
        if self.state_byte63&1:return self.phase
        clock=f32(inputs.seconds)
        delta=max(0.,f32(f32(self.rate2*self.rate1)*f32(clock-self.previous_clock)))
        self.previous_clock=clock
        phase=f32(self.phase-delta if self.reverse else self.phase+delta)
        # Exact endpoints remain active. Crossing an endpoint clamps and stops.
        if phase<self.lower:
            phase=self.lower;self.state_byte63=3
        elif phase>self.upper:
            phase=self.upper;self.state_byte63=3
        self.phase=phase
        return phase

    def request(self, inputs):
        return self.consumer.request(inputs)
