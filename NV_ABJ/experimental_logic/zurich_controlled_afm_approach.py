

class ZurichApproaches:
    """This class was made for use with LTSPM and has only been thoroughly used on LTSPM2 with 
    JPEs and a attocube z scanner 
    """

    def __init__(self, scanner_device, positioner_device, ):
        scanner_z_voltage_minimum = 
        scanner_z_voltage_maximum = 8
        scanner_z_step_size = 5e-3
        scanner_z_voltage_retract_full = True

        scanner_retract_voltage = 1

        scanner_z_step_delay_s = .05
        scanner_retracting_step_size = 100e-3

        afm_magnitude_percent_deviation_from_normal = .25e-3

        jpe_z_steps = 100

        zurich_afm_connection = 


    def MacroscopicApproach():
        z_voltages = np.arange(z_voltage_minimum,z_voltage_maximum,z_step_size)
        ZurichTF = ZurichTuningFork(ip_address=zuric_ip_address,tf_data_path=tuning_fork_data_path,name=zuric_name,device=zuric_device,aux=aux_location)

        x,y = ZurichTF.get_tuning_fork_data(poll_length=0.1)
        initial_measurement = np.mean(y)
        print(f"Initial Voltage(mV): {initial_measurement*1000}")
        global not_contact
        not_contact = True

        import requests

        def send_slack_message(message,webhook):
            payload = '{"text":"%s"}' % message
            response = requests.post(webhook,data=payload)
            return response.text


        webhook = "https://hooks.slack.com/services/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"
        print(send_slack_message(webhook=webhook,message="Starting AFM Approach"))

        def contact():
            x,y = ZurichTF.get_tuning_fork_data(poll_length=0.1)
            current_measurement = np.mean(y)
            
            if initial_measurement+deviation_from_initial_reading_v > current_measurement and initial_measurement-deviation_from_initial_reading_v < current_measurement:
                return False 
            else:
                return True 
                

        while not_contact:
            print("Scanning Voltages")
            for z in z_voltages:
                if contact():
                    print(z)
                    print("In Contact")
                    not_contact = False
                    final_contact_voltage = z
                    break
                
                with scanner_z:
                    scanner_z.wait_for_voltage(z)
                
                time.sleep(z_step_delay)
                print(f"Voltage:{z}",end="\r")
            else:
                print("\nRetracting")
                with scanner_z:
                    for z in reversed(z_voltages[::10]):
                        scanner_z.wait_for_voltage(z)
                        time.sleep(z_step_delay)
                        print(f"Voltage:{z}",end="\r")
                    scanner_z.wait_for_voltage(0)
                    print(f"Voltage:{z}",end="\r")
                print("\nIncreasing Z JPE")
                with inner_z_jpe:
                    inner_z_jpe.move_positioner(1,jpe_z_steps)
                
                time.sleep(30)

                if contact():
                    print(z)
                    # final_contact_voltage = z
                    not_contact = False
                    break

                continue



            print("exiting loop")

            retract_voltage = np.arange(final_contact_voltage,0,z_step_size)
            for z in reversed(retract_voltage):
                
                with scanner_z:
                    scanner_z.wait_for_voltage(z)
                
                time.sleep(z_step_delay)
                print(f"Voltage:{z}",end="\r")

            with scanner_z:
                scanner_z.wait_for_voltage(0)

            break
        print(send_slack_message(webhook=webhook,message=f"Contact happened at {final_contact_voltage}"))

        print(f"Contact happened at {final_contact_voltage}")
    
    def PL_vs_Z_approach():

        z_voltages = np.arange(z_voltage_minimum,z_voltage_maximum,z_step_size)
        ZuricTF = ZuricTuningFork(ip_address=zuric_ip_address,tf_data_path=tuning_fork_data_path,name=zuric_name,device=zuric_device,aux=aux_location)

        x,y = ZuricTF.get_tuning_fork_data(poll_length=0.1)
        initial_measurement = np.mean(y)
        print(f"Initial Voltage: {initial_measurement*1000} mV")

        not_contact = True

        counts = []
        measured_z_voltage = []

        def contact():
            x,y = ZuricTF.get_tuning_fork_data(poll_length=0.1)
            current_measurement = np.mean(y)
            
            if initial_measurement+deviation_from_initial_reading_v > current_measurement and initial_measurement-deviation_from_initial_reading_v < current_measurement:
                return False 
            else:
                return True 

            # raise Exception("Failed to connect to the Zurich. Sample has been retracted using the scanner")

        print("Scanning Voltages")

        # with scanner_z, photon_counter_1 as pc:
        for z in z_voltages:
            if contact():
                print(z)
                print("In Contact") 
                final_contact_voltage = z
                break

            with photon_counter_1 as pc:
                counts.append(pc.get_counts_per_second(30e-3))
            with scanner_z:
                measured_z_voltage.append(scanner_z.read_voltage())
                scanner_z.wait_for_voltage(z)
                
            time.sleep(z_step_delay)
            print(f"Voltage:{z}",end="\r")



        print("\nRetracting After Contact")
        retract_voltage = np.flip(np.arange(0,final_contact_voltage,z_step_size*10))

        for z in retract_voltage:

            with scanner_z:
                scanner_z.wait_for_voltage(z)
            
            time.sleep(z_step_delay)
            print(f"Voltage:{z}",end="\r")

        with scanner_z:
            scanner_z.wait_for_voltage(0)
            print(f"Voltage:0",end="\r")
        print(f"\nContact happened at {final_contact_voltage}")
                

        plt.plot(np.array(max(z_voltages[:len(counts)]) - np.array(z_voltages[:len(counts)]))*10/8,np.array(counts)/1000, color="peachpuff")
        plt.xlabel("Estimated Distance(um)")
        plt.ylabel("kCounts/s")
        plt.title("Approach Curve")
        plt.show()
        print(send_slack_message(webhook=webhook,message=f"Contact happened at {final_contact_voltage}"))

