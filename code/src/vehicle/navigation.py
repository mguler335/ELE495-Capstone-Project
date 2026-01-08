import json
import time
import os
import sys

#Add paths for flexible imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

try:
    #Try relative imports first (when running from src directory)
    from vehicle.motor_control import MotorController
    from vehicle.sensors import MPU6050, UltrasonicSensor
    from vehicle.pid_control import PIDController
except ImportError:
    #Fallback to absolute imports (when running from project root)
    from src.vehicle.motor_control import MotorController
    from src.vehicle.sensors import MPU6050, UltrasonicSensor
    from src.vehicle.pid_control import PIDController


def execute_commands(status_server=None):
    """Execute vehicle commands from JSON file (renamed from arac_kontrol_2surucu_tankmod.main)"""
    motor_controller = MotorController()
    mpu = MPU6050()

    if os.path.basename(os.getcwd()) == 'src':
        # Running from src directory
        data_dir = '../data'
    else:
        # Running from project root
        data_dir = 'data'
    
    #Ultrasonic sensors
    TRIG_ON = 5
    ECHO_ON = 6
    TRIG_ARKA = 16
    ECHO_ARKA = 24
    
    front_sensor = UltrasonicSensor(TRIG_ON, ECHO_ON)
    rear_sensor = UltrasonicSensor(TRIG_ARKA, ECHO_ARKA)
    
    try:
        #Determine correct path for commands.json
        if os.path.basename(os.getcwd()) == 'src':
            commands_file = "../config/commands.json"
        else:
            commands_file = "config/commands.json"
            
        with open(commands_file, "r") as f:
            komutlar = json.load(f)
        
        for komut in komutlar:
            try:
                hiz = komut['hiz']
            except:
                hiz = 0

            try:
                uygulanacak_komut = komut['komut']
            except:
                uygulanacak_komut = 'dur'
            
            try:
                aci = komut['aci']
            except:
                aci = 0

            try:
                kosul = komut['kosul']
            except:
                kosul = 'engel_algilayana_kadar'

            #Update status to indicate movement is starting
            if status_server:
                status_server.update_vehicle_state("executing")

            #Recalibrate gyro between commands to prevent drift
            if uygulanacak_komut in ["sola_don", "saga_don"]:
                mpu.calibrate_gyro()
            
            execute_movement(uygulanacak_komut, motor_controller, mpu, front_sensor, rear_sensor, hiz, kosul, aci, status_server)

        #Update status to indicate all commands are completed
        if status_server:
            status_server.update_vehicle_state("tamamlandi")
            
        #Clear the commands file after all commands are executed
        with open(commands_file, "w") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        response_audio_file = os.path.join(data_dir, 'gorev_tamamlandi.mp3')
        os.system(f"mpg123 {response_audio_file}") 
        print("✅ Komutlar tamamlandı, JSON dosyası temizlendi.")

    finally:
        motor_controller.cleanup()


def execute_movement(komut, motor_controller, mpu, front_sensor, rear_sensor, hiz=0, kosul="engele 50 cm kalana kadar", aci=0, status_server=None):
    """Execute individual movement command"""

    if os.path.basename(os.getcwd()) == 'src':
        # Running from src directory
        data_dir = '../data'
    else:
        # Running from project root
        data_dir = 'data'
    
    
    #Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)

    if komut == "ileri_git":
        if status_server:
            status_server.update_vehicle_state("ileri_gidiliyor")
            
        response_audio_file = os.path.join(data_dir, 'ileri_gidis.mp3')
        os.system(f"mpg123 {response_audio_file}") 
        
        if 'engele' in kosul:
            kosullar = kosul.split(' ')
            mesafe = int(kosullar[1])
            while front_sensor.measure_distance() > mesafe:
                motor_controller.move_forward(hiz)
                print(f"Distance: {front_sensor.measure_distance():.1f}cm")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")
        elif 'saniye' in kosul:
            kosullar = kosul.split(' ')
            duration = int(kosullar[0])
            start_time = time.time()
            mesafe = 10  #Minimum distance in cm
            
            while (time.time() - start_time < duration) and (front_sensor.measure_distance() > 50):
                motor_controller.move_forward(hiz)
                print(f"Time: {time.time() - start_time:.1f}s")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")
        elif 'metre' in kosul:
            print('METREYE GİRDİ')
            ort_hiz = 93
            kosullar = kosul.split(' ')
            mesafe = int(kosullar[0])
            duration_m = ort_hiz/mesafe
            print(kosullar, mesafe)
            print(duration_m)
            start_time = time.time()
            
            while (time.time() - start_time < duration_m) and (rear_sensor.measure_distance() > 50):
                motor_controller.move_forward(hiz)
                # print(f"Mesafe: {ort_hiz / int(time.time() - start_time):.1f}")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")
        
    elif komut == "geri_git":
        if status_server:
            status_server.update_vehicle_state("geri_gidiliyor")
            
        response_audio_file = os.path.join(data_dir, 'geri_gidis.mp3')
        os.system(f"mpg123 {response_audio_file}") 
        if 'engele' in kosul:
            kosullar = kosul.split(' ')
            mesafe = int(kosullar[1])
            while rear_sensor.measure_distance() > mesafe:
                motor_controller.move_backward(hiz)
                print(f"Distance: {rear_sensor.measure_distance():.1f}cm")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")
        elif 'saniye' in kosul:
            kosullar = kosul.split(' ')
            duration = int(kosullar[0])
            start_time = time.time()
            mesafe = 10  #Minimum distance in cm
            
            while (time.time() - start_time < duration) and (rear_sensor.measure_distance() > 50):
                motor_controller.move_backward(hiz)
                print(f"Time: {time.time() - start_time:.1f}s")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")
        elif 'metre' in kosul:
            ort_hiz = 93
            kosullar = kosul.split(' ')
            mesafe = int(kosullar[0])
            duration_m = ort_hiz/mesafe
            print(kosullar, mesafe)
            print(duration_m)
            start_time = time.time()
            
            while (time.time() - start_time < duration_m) and (rear_sensor.measure_distance() > 50):
                motor_controller.move_backward(hiz)
                # print(f"Mesafe: {ort_hiz / int(time.time() - start_time):.1f}")
                time.sleep(0.01)
            motor_controller.stop()
            if status_server:
                status_server.update_vehicle_state("bekliyor")


        
    elif komut in ["sola_don", "saga_don"]:
        if status_server:
            status_server.update_vehicle_state("donuyor")
            
        hedef_aci = aci
        toplam_aci = 0
        direction_text = "sola" if komut == "sola_don" else "saga"
        
        #Gyro is already calibrated before this function
        
        #Play audio once before starting turn
        if komut == "sola_don":
            response_audio_file = os.path.join(data_dir, 'sola_donus.mp3')
            os.system(f"mpg123 {response_audio_file}") 
        elif komut == "saga_don":
            response_audio_file = os.path.join(data_dir, 'sag_donus.mp3')
            os.system(f"mpg123 {response_audio_file}") 
        
        #PID controller for angle control - Testing new parameters for overshoot
        angle_pid = PIDController(kp=0.9, ki=0.4, kd=0.9, setpoint=hedef_aci, output_limits=(45, 80))

        onceki_zaman = time.time()
        tolerance = 1.5
        overshoot_tolerance = 0.5  #Smaller tolerance for overshoot detection
        max_overshoot_corrections = 5  #Allow more corrections but with better logic
        overshoot_corrections = 0
        last_correction_direction = None
        oscillation_count = 0
        
        while True:
            current_angle = abs(toplam_aci)
            error = hedef_aci - current_angle
            
            #Check if we're within tolerance, but account for coasting
            #Stop earlier to compensate for robot momentum
            coast_compensation = 3.0  #Estimated degrees robot will coast
            if abs(error) <= tolerance + coast_compensation:
                break
            
            #Handle overshoot correction with oscillation detection
            if error < -overshoot_tolerance and overshoot_corrections < max_overshoot_corrections:
                #Determine correction direction (opposite of original turn)
                correction_direction = "saga_don" if komut == "sola_don" else "sola_don"
                
                #Check for oscillation (alternating correction directions)
                if last_correction_direction and last_correction_direction != correction_direction:
                    oscillation_count += 1
                    print(f"Oscillation detected #{oscillation_count}")
                    if oscillation_count >= 2:
                        print("Stopping corrections to prevent oscillation")
                        break
                
                overshoot_corrections += 1
                last_correction_direction = correction_direction
                correction_needed = abs(error)
                
                print(f"Overshoot correction #{overshoot_corrections}: {current_angle:.1f}° -> {hedef_aci}°")
                
                #Reduce correction power if multiple corrections have been made
                correction_power_multiplier = max(0.7, 1.0 - (overshoot_corrections - 1) * 0.15)
                min_power = int(50 * correction_power_multiplier)
                max_power = int(70 * correction_power_multiplier)
                
                #Use PID for correction with adaptive power
                correction_pid = PIDController(kp=0.8, ki=0.0, kd=0.3, setpoint=0, output_limits=(min_power, max_power))
                
                correction_start_time = time.time()
                correction_timeout = min(correction_needed / 40.0, 1.2)  #Shorter timeout for later corrections
                
                #Correction loop with PID
                while (abs(error) > tolerance and 
                       time.time() - correction_start_time < correction_timeout):
                    
                    current_error = hedef_aci - abs(toplam_aci)
                    correction_speed = correction_pid.update(-current_error)  #Negative because we want to reduce error
                    
                    if correction_direction == "sola_don":
                        motor_controller.tank_turn_left(correction_speed)
                    else:
                        motor_controller.tank_turn_right(correction_speed)
                    
                    simdi = time.time()
                    dt = simdi - onceki_zaman
                    onceki_zaman = simdi
                    
                    gyro_z = mpu.get_gyro_z()
                    if komut == "saga_don":
                        toplam_aci += gyro_z * dt
                    else:
                        toplam_aci -= gyro_z * dt
                    
                    error = hedef_aci - abs(toplam_aci)
                    time.sleep(0.01)
                
                motor_controller.stop()
                time.sleep(0.15)  #Longer settling time after correction
                continue
                
            #Normal turning
            if error > tolerance:
                motor_hiz = angle_pid.update(current_angle)
                
                #Progressive speed reduction as we approach target for smoother stopping
                if error < 8:
                    motor_hiz = max(motor_hiz * 0.8, 45)
                elif error < 15:
                    motor_hiz = max(motor_hiz * 0.9, 50)

                if komut == "sola_don":
                    motor_controller.tank_turn_left(motor_hiz)    
                elif komut == "saga_don":
                    motor_controller.tank_turn_right(motor_hiz)
            else:
                break
                
            simdi = time.time()
            dt = simdi - onceki_zaman
            onceki_zaman = simdi
            
            gyro_z = mpu.get_gyro_z()
            if komut == "saga_don":
                toplam_aci += gyro_z * dt
            else:
                toplam_aci -= gyro_z * dt
            
            if abs(toplam_aci) % 10 < 1:  #Print every ~10 degrees
                print(f"Angle: {abs(toplam_aci):.1f}°/{hedef_aci}°")
            time.sleep(0.01)
        
        motor_controller.stop()
        
        #Measure for a short time to capture actual final position after coasting
        settling_start = time.time()
        while time.time() - settling_start < 0.2:  #Reduced from 0.3 to 0.2 seconds
            simdi = time.time()
            dt = simdi - onceki_zaman
            onceki_zaman = simdi
            
            gyro_z = mpu.get_gyro_z()
            if komut == "saga_don":
                toplam_aci += gyro_z * dt
            else:
                toplam_aci -= gyro_z * dt
            time.sleep(0.01)
        
        final_angle = abs(toplam_aci)
        final_error = hedef_aci - final_angle
        print(f"{direction_text} {hedef_aci}° dönüş tamamlandı. Final angle: {final_angle:.2f}°")
        
        #Final overshoot check with oscillation protection
        if final_angle > hedef_aci + 3.0 and oscillation_count < 2:  #Only correct if no oscillation detected
            print(f"Final overshoot detected: {final_angle:.1f}° > {hedef_aci}°, correcting...")
            correction_direction = "saga_don" if komut == "sola_don" else "sola_don"
            overshoot_amount = final_angle - hedef_aci
            
            #Use conservative correction to prevent new oscillations
            correction_angle_needed = overshoot_amount * 0.6  #More conservative
            correction_pid = PIDController(kp=0.8, ki=0.0, kd=0.25, setpoint=hedef_aci, output_limits=(45, 65))
            
            correction_start = time.time()
            correction_start_angle = abs(toplam_aci)
            
            while (abs(toplam_aci) > hedef_aci + 2.0 and 
                   time.time() - correction_start < 1.5 and
                   abs(correction_start_angle - abs(toplam_aci)) < correction_angle_needed):
                
                current_angle = abs(toplam_aci)
                correction_speed = correction_pid.update(current_angle)
                
                if correction_direction == "sola_don":
                    motor_controller.tank_turn_left(correction_speed)
                else:
                    motor_controller.tank_turn_right(correction_speed)
                
                simdi = time.time()
                dt = simdi - onceki_zaman
                onceki_zaman = simdi
                
                gyro_z = mpu.get_gyro_z()
                if komut == "saga_don":
                    toplam_aci += gyro_z * dt
                else:
                    toplam_aci -= gyro_z * dt
                time.sleep(0.01)
            
            motor_controller.stop()
            time.sleep(0.1)  #Brief settling
            print(f"Final correction completed. New angle: {abs(toplam_aci):.2f}°")
        elif oscillation_count >= 2:
            print(f"Skipping final correction due to oscillation prevention. Final angle: {final_angle:.2f}°")
            
        if status_server:
            status_server.update_vehicle_state("bekliyor")
            
    elif komut == "yaklasma":
        if status_server:
            status_server.update_vehicle_state("yaklasiyor")
        target_distance = int(kosul.split('cm')[0])

        #PID logic
        distance_pid = PIDController(kp=1.0, ki=0.0, kd=0.1, setpoint=target_distance, output_limits=(15, 60))
        current_distance = front_sensor.measure_distance()
        while abs(current_distance - target_distance) > 2:
            current_distance = front_sensor.measure_distance()
            speed = distance_pid.update(current_distance)
            motor_controller.move_forward(speed)
            
            error = abs(current_distance - target_distance)
            print(f"Distance Approach - Current: {current_distance:.1f}cm, Target: {target_distance}cm, Error: {error:.1f}cm, Speed: {speed:.0f}")
            time.sleep(0.01)

        motor_controller.stop()
        #Wait for mechanical settling
        time.sleep(0.1)
        if status_server:
            status_server.update_vehicle_state("bekliyor")
        print(f"İleri yaklaşma tamamlandı! {target_distance}cm mesafede duruldu.")
    elif komut == "yaklasma_geri":
        if status_server:
            status_server.update_vehicle_state("approaching_backward")
        target_distance = int(kosul.split('cm')[0])

        #PID logic
        distance_pid = PIDController(kp=1.0, ki=0.0, kd=0.1, setpoint=target_distance, output_limits=(15, 60))
        current_distance = rear_sensor.measure_distance()
        while abs(current_distance - target_distance) > 2:
            current_distance = rear_sensor.measure_distance()
            speed = distance_pid.update(current_distance)
            motor_controller.move_backward(speed)
            
            error = abs(current_distance - target_distance)
            print(f"Backward Distance Approach - Current: {current_distance:.1f}cm, Target: {target_distance}cm, Error: {error:.1f}cm, Speed: {speed:.0f}")
            time.sleep(0.01)

        motor_controller.stop()
        #Wait for mechanical settling
        time.sleep(0.1)
        if status_server:
            status_server.update_vehicle_state("bekliyor")
        print(f"Geri yaklaşma tamamlandı! {target_distance}cm mesafede duruldu.")
    
    elif komut == "mesafe_ileri":
        if status_server:
            status_server.update_vehicle_state("masefe_ileri")
        if "metre" in kosul:
            target_distance = int(kosul.split('_')[0]) * 100
        elif "cm" in kosul:
            target_distance = int(kosul.split('_')[0])

        #Track distance using sensor data.
        start_position = front_sensor.measure_distance()
        distance_travelled = 0

        distance_pid = PIDController(kp=1.0, ki=0.0, kd=0.1, setpoint=target_distance, output_limits=(20, hiz))

        #PID loop
        while distance_travelled < target_distance - 5:
            current_position = front_sensor.measure_distance()
            distance_travelled = start_position - current_position
            remaining = target_distance - distance_travelled
            speed = distance_pid.update(distance_travelled)

            motor_controller.move_forward(speed)

            print(f"Distance Movement - Traveled: {distance_travelled:.1f}cm, Target: {target_distance}cm, Remaining: {remaining:.1f}cm, Speed: {speed:.0f}")
            time.sleep(0.01)

        motor_controller.stop()
        #Wait for mechanical settling
        time.sleep(0.1)
        if status_server:
            status_server.update_vehicle_state("bekliyor")
        print(f"Mesafe hareketi tamamlandı! {target_distance}cm ileri gidildi.")

    elif komut == "mesafe_geri":
        if status_server:
            status_server.update_vehicle_state("geri_mesafe")
        if "metre" in kosul:
            target_distance = int(kosul.split('_')[0]) * 100
        elif "cm" in kosul:
            target_distance = int(kosul.split('_')[0])

        #Track distance using sensor data.
        start_position = rear_sensor.measure_distance()
        distance_travelled = 0

        distance_pid = PIDController(kp=1.0, ki=0.0, kd=0.1, setpoint=target_distance, output_limits=(20, hiz))

        #PID loop
        while distance_travelled < target_distance - 5:
            current_position = rear_sensor.measure_distance()
            distance_travelled = start_position - current_position
            remaining = target_distance - distance_travelled
            speed = distance_pid.update(distance_travelled)

            motor_controller.move_backward(speed)

            print(f"Distance Movement - Traveled: {distance_travelled:.1f}cm, Target: {target_distance}cm, Remaining: {remaining:.1f}cm, Speed: {speed:.0f}")
            time.sleep(0.01)

        motor_controller.stop()
        #Wait for mechanical settling
        time.sleep(0.1)
        if status_server:
            status_server.update_vehicle_state("bekliyor")
        print(f"Mesafe hareketi tamamlandı! {target_distance}cm geri gidildi.")

