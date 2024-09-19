'''
prometheus module defines application metrices for the application
'''

from prometheus_client import Counter, Enum, Gauge, Histogram, Info, Summary

class Metrices:

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_counter(name: str, description: str, labelnames: list = None) -> Counter:
        if labelnames is not None:
            counter = Counter(name=name, documentation=description, labelnames=labelnames)
        else:
            counter = Counter(name=name, documentation=description)
        return counter
    
    def get_gauge(self, name: str, description: str) -> Gauge:
        gauge = Gauge(name=name, documentation=description)
        return gauge
    
    def get_summary(self, name: str, description: str) -> Summary:
        summary = Summary(name=name, documentation=description)
        return summary

    def get_info(self, name: str, description: str) -> Info:
        info = Info(name=name, documentation=description)
        return info
    
    def get_enum(self, name: str, description: str, states: list) -> Enum:
        enum = Enum(name=name, documentation=description, states=states)
        return enum
    
    def get_histogram(self, name: str, description: str) -> Histogram:
        histogram = Histogram(name=name, documentation=description)
        return histogram
    