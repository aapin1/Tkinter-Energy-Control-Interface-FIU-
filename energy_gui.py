import socket
import tkinter as tk
from tkinter import messagebox

#defining power supplies with IP's and ports
power_supplies = {
    "Power Supply 1": ("192.168.5.102", 5008),
    "Power Supply 2": ("192.168.5.101", 50505),
    "Power Supply 3": ("192.168.5.104", 8899)
}

#setting global variables
sock = None
host = ""
port = 0
current_voltage = ""
current_current = ""

#defining the maximum and minimum volt/current
MAX_VOLTAGE = 150
MAX_CURRENT = 10
MIN_VALUE = 0

def send_command(command):
    #send a string command to the connected socket
    global sock
    try:
        if sock:
            sock.send(command.encode() + b"\n")
            log(f"Sent: {command}")
        else:
            log("Not connected.")
    except Exception as e:
        log(f"Error sending '{command}': {e}")

def log(msg):
    #display messages in the output text box
    output_box.insert(tk.END, msg + "\n")
    output_box.see(tk.END)

def clamp_value(value, max_val):
    #restrict the value between MIN_VALUE and max_val
    try:
        val = float(value)
        if val < MIN_VALUE:
            return str(MIN_VALUE)
        elif val > max_val:
            return str(max_val)
        return str(val)
    except ValueError:
        return str(MIN_VALUE)

def on_power_select(selection):
    #handle power supply selection from dropdown
    global host, port, sock

    if selection not in power_supplies:
        messagebox.showerror("Error", "Invalid power supply selected.")
        return

    host, port = power_supplies[selection]
    current_label.config(text=f"Connected to: {selection}")

    if sock:
        try:
            sock.close()
            log("Closed previous connection.")
        except Exception as e:
            log(f"Error closing socket: {e}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        log(f"Connected to {selection} at {host}:{port}")
        start_frame.pack()
        control_frame.pack_forget()
        restart_frame.pack_forget()
    except socket.timeout:
        log(f"Timeout: Cannot connect to {host}:{port}")
        sock = None
    except Exception as e:
        log(f"Connection failed: {e}")
        sock = None

def start_output():
    #start output with initial voltage/current
    global current_voltage, current_current
    current_voltage = clamp_value(voltage_entry.get(), MAX_VOLTAGE)
    current_current = clamp_value(current_entry.get(), MAX_CURRENT)
    send_command(f"VOLT {current_voltage}")
    send_command(f"CURR {current_current}")
    send_command("OUTP:START")
    control_frame.pack()

def apply_voltage():
    #apply a new voltage value
    global current_voltage
    current_voltage = clamp_value(voltage_entry.get(), MAX_VOLTAGE)
    send_command(f"VOLT {current_voltage}")
    log(f"Voltage set to {current_voltage}V")

def apply_current():
    #apply a new current value.
    global current_current
    current_current = clamp_value(current_entry.get(), MAX_CURRENT)
    send_command(f"CURR {current_current}")
    log(f"Current set to {current_current}A")

def stop_output():
    #stop output and offer disconnect/restart options.
    global sock
    send_command("OUTP:STOP")
    if messagebox.askyesno("Disconnect?", "Disconnect from power supply?"):
        send_command("SYST:LOC")
        if sock:
            try:
                sock.close()
                log("Disconnected from power supply.")
                sock = None
            except Exception as e:
                log(f"Error during disconnect: {e}")
        #reset UI to initial state
        current_label.config(text="No Power Supply Connected")
        power_var.set("Select...")
        start_frame.pack_forget()
        control_frame.pack_forget()
        restart_frame.pack_forget()
    elif messagebox.askyesno("Restart Output?", "Restart the output?"):
        restart_frame.pack()
    else:
        log("Output stopped, not disconnected.")

def restart_output():
    #restart output with new voltage/current.
    global current_voltage, current_current
    current_voltage = clamp_value(restart_voltage_entry.get(), MAX_VOLTAGE)
    current_current = clamp_value(restart_current_entry.get(), MAX_CURRENT)
    send_command(f"VOLT {current_voltage}")
    send_command(f"CURR {current_current}")
    send_command("OUTP:START")
    log("Output restarted.")
    restart_frame.pack_forget()

#setting up the GUI
root = tk.Tk()
root.title("Magna Power Supply Controller")

#making the dropdown selector
tk.Label(root, text="Select Power Supply:").pack(pady=5)
power_var = tk.StringVar(root)
power_var.set("Select...")

def power_selected_callback(*args):
    selection = power_var.get()
    if selection != "Select...":
        on_power_select(selection)

power_var.trace_add("write", power_selected_callback)
power_menu = tk.OptionMenu(root, power_var, *power_supplies.keys())
power_menu.pack(pady=5)

#connection status label (connected to something or no)
current_label = tk.Label(root, text="No Power Supply Connected")
current_label.pack(pady=5)

#exit the entire program button
tk.Button(root, text="Exit Program", command=root.quit).pack(pady=5)

#start frame (initial settings)
start_frame = tk.Frame(root)
tk.Label(start_frame, text="Initial Voltage:").grid(row=0, column=0)
voltage_entry = tk.Entry(start_frame)
voltage_entry.grid(row=0, column=1)

tk.Label(start_frame, text="Initial Current:").grid(row=1, column=0)
current_entry = tk.Entry(start_frame)
current_entry.grid(row=1, column=1)

tk.Button(start_frame, text="Start Output", command=start_output).grid(row=2, column=0, columnspan=2, pady=5)

#control the frame (adjustments)
control_frame = tk.Frame(root)
tk.Label(control_frame, text="Adjust Voltage:").grid(row=0, column=0)
tk.Button(control_frame, text="Apply", command=apply_voltage).grid(row=0, column=1)

tk.Label(control_frame, text="Adjust Current:").grid(row=1, column=0)
tk.Button(control_frame, text="Apply", command=apply_current).grid(row=1, column=1)

tk.Button(control_frame, text="Stop Output", command=stop_output).grid(row=2, column=0, columnspan=2, pady=5)

#restart the frame (new settings)
restart_frame = tk.Frame(root)
tk.Label(restart_frame, text="New Voltage:").grid(row=0, column=0)
restart_voltage_entry = tk.Entry(restart_frame)
restart_voltage_entry.grid(row=0, column=1)

tk.Label(restart_frame, text="New Current:").grid(row=1, column=0)
restart_current_entry = tk.Entry(restart_frame)
restart_current_entry.grid(row=1, column=1)

tk.Button(restart_frame, text="Restart Output", command=restart_output).grid(row=2, column=0, columnspan=2, pady=5)

#define the output log Box
output_box = tk.Text(root, height=12, width=50)
output_box.pack(pady=10)

#start GUI event loop
root.mainloop()
