from __future__ import annotations  # Must be at the top of the file

class Interval:
    """
    Represents an interval with a start and end time.
    """
    def __init__(self, start: int =0, end: int =0, activity_type : str ="proposed_safari_beginning"):
        self.start = start
        self.end = end
        self.activity_type = activity_type  # e.g., "safari" or "palace"

    def overlaps_with(self, other: Interval):
        """
        Check if this interval overlaps with another interval.
        """
        return not (self.end <= other.start or other.end <= self.start)

    def to_dict(self):
        """
        Convert the interval to a dictionary with activity-specific keys.
        """
        if self.activity_type == "safari":
            return {
                "proposed_safari_beginning": self.start,
                "proposed_safari_end": self.end
            }
        elif self.activity_type == "palace":
            print("tutaj jestem", self.start)
            return {
                "proposed_palace_beginning": self.start,
                "proposed_palace_end": self.end
            }
        else:
            raise ValueError("Invalid activity type")