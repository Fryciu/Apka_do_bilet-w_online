class RecursionTrigger(Exception):
    """Custom exception to handle pseudo-recursion."""
    pass

recursion_points = {}

def set_recursion(id):
    """Mark a point in the code for recursion."""
    recursion_points[id] = None  # Placeholder for execution state
    try:
        yield  # Yield control to allow execution to proceed
    except RecursionTrigger:
        pass  # When recursion is triggered, execution resumes here

def trigger_recursion(id):
    """Trigger a return to the marked recursion point."""
    if id in recursion_points:
        raise RecursionTrigger  # Jump back to the set_recursion point
    else:
        raise ValueError(f"No recursion point found for ID {id}")

# Example usage
i = 0
gen = set_recursion(435665)  # Create generator for recursion
next(gen)  # Start execution

while True:
    i += 1
    print(i)
    
    if i >= 10:
        break  # Stop when i reaches 10
    else:
        trigger_recursion(435665)  # Jump back
