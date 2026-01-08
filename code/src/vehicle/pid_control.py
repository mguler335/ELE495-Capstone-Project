import time

class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0, output_limits=(25, 100)):
        #PID gains
        self.kp = kp
        self.ki = ki
        self.kd = kd

        #Target
        self.setpoint = setpoint
        
        #Output limits
        self.output_limits = output_limits

        #Internal state
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = None

    def update(self, current_value, dt=None):
        #Calculate error.
        error = self.setpoint - current_value

        #Calculate time difference.
        current_time = time.time()
        if self.last_time is None:
            self.last_time = current_time
            return 0.0
        dt = current_time - self.last_time
        self.last_time = current_time

        #Calculate the PID terms.
        #Proportional:
        p_term = self.kp * error
        #Integral:
        self.integral += error * dt
        i_term = self.ki * self.integral
        #Derivative:
        d_term = self.kd * (error - self.previous_error) / dt

        #Update error.
        self.previous_error = error

        #Combine the PID terms.
        output = p_term + i_term + d_term
        
        #Apply output limits.
        if self.output_limits:
            min_limit, max_limit = self.output_limits
            output = max(min_limit, min(output, max_limit))
        
        return output

        


