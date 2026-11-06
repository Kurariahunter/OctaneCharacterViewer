"""Verified normal-mode clock arithmetic; caller controls scheduling explicitly.

This models clock inputs and lazy publication, not clip boundaries or game threads.
"""
from dataclasses import dataclass
import struct

def f32(value):
    return struct.unpack('<f',struct.pack('<f',value))[0]

@dataclass(frozen=True)
class ClockInputs:
    seconds: float
    delta_seconds: float
    token: int
    generation: int

class DefaultEngineClock:
    def __init__(self, *, total_ms=0, token=0, cap_ms=100):
        for name,value in [('total_ms',total_ms),('token',token),('cap_ms',cap_ms)]:
            if type(value) is not int or not 0<=value<=0xffffffff:
                raise ValueError(name+' must be uint32')
        self.total_ms=total_ms
        self.token=token
        self.cap_ms=cap_ms
        self.raw_delta_ms=self.effective_delta_ms=17
        self.previous_seconds=0.
        self.seconds=f32(total_ms*.001)
        self.delta_seconds=f32(.017)
        self.generation=0
        self.published=None

    def advance(self, raw_delta_ms):
        if type(raw_delta_ms) is not int or not 0<=raw_delta_ms<=0xffffffff:
            raise ValueError('raw_delta_ms must be uint32')
        self.raw_delta_ms=raw_delta_ms
        self.effective_delta_ms=min(raw_delta_ms,self.cap_ms)
        self.total_ms=(self.total_ms+self.effective_delta_ms)&0xffffffff
        self.previous_seconds=self.seconds
        self.seconds=f32(self.total_ms*.001)
        self.delta_seconds=f32(self.effective_delta_ms*f32(.001))
        self.token=(self.token+1)&0xffffffff
        # Advancing the owner does not publish its new values automatically.

    def publish(self):
        self.generation+=1
        self.published=ClockInputs(self.seconds,self.delta_seconds,self.token,self.generation)
        return self.published

class DemandClockConsumer:
    """Minimal lazy input cache; evaluator owns native clip-time semantics.

    Generation is an unbounded adapter invalidation serial, not the native
    16-bit metadata stamp. It must never be exported as a game field.
    """
    def __init__(self, evaluator):
        self.evaluator=evaluator
        self.generation=None
        self.inputs=None
        self.value=None
        self.evaluations=0

    def request(self, inputs):
        if inputs is None:
            raise ValueError('Publish clock inputs before requesting evaluation')
        if inputs is not self.inputs:
            self.value=self.evaluator(inputs)
            self.inputs=inputs
            self.generation=inputs.generation
            self.evaluations+=1
        return self.value
