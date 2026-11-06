"""Bounded AnimCurveControlProcessor arithmetic for native boundary byte 0x0E."""
import math
from native_default_clock import f32,DemandClockConsumer

class CyclicCurveTime:
    def __init__(self, lower, upper, *, phase=None, previous_clock=0., rate1=1., rate2=1., reverse=False):
        values=[lower,upper,previous_clock,rate1,rate2]
        if phase is not None:values.append(phase)
        if not all(math.isfinite(v) for v in values):raise ValueError('Finite values required')
        self.lower,self.upper=f32(lower),f32(upper)
        if self.upper<=self.lower:raise ValueError('Positive float32 clip range required')
        self.phase=f32(self.lower if phase is None else phase)
        if not self.lower<=self.phase<=self.upper:raise ValueError('Initial phase outside clip range')
        self.previous_clock=f32(previous_clock)
        self.rate1,self.rate2=f32(rate1),f32(rate2)
        self.reverse=bool(reverse)
        self.consumer=DemandClockConsumer(self._evaluate)

    def _evaluate(self, inputs):
        clock=f32(inputs.seconds)
        delta=max(0.,f32(f32(self.rate2*self.rate1)*f32(clock-self.previous_clock)))
        self.previous_clock=clock
        phase=f32(self.phase-delta if self.reverse else self.phase+delta)
        span=f32(self.upper-self.lower)
        if phase<self.lower:
            distance=f32(self.lower-phase)
            if distance>span:distance=f32(math.fmod(distance,span))
            phase=f32(self.upper-distance)
        elif phase>self.upper:
            distance=f32(phase-self.upper)
            if distance>span:distance=f32(math.fmod(distance,span))
            phase=f32(self.lower+distance)
        self.phase=phase
        return phase

    def request(self, published_inputs):
        return self.consumer.request(published_inputs)
